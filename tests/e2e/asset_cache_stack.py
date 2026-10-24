"""Run an owned image-switching fixture with nginx's real HTTP cache."""

import http.client
import json
import os
import shlex
import signal
import socket
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from uuid import uuid4

NGINX = "sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10"
EXPECTED = (RuntimeError, OSError, subprocess.SubprocessError)


@contextmanager
def fixture_signals():
    """Unwind fixture contexts on TERM/INT, restoring the caller's handlers."""

    def interrupted(_signum, _frame):
        raise RuntimeError("fixture_interrupted")

    previous = {
        sig: signal.signal(sig, interrupted) for sig in (signal.SIGTERM, signal.SIGINT)
    }
    try:
        yield
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


class RequestGate(BaseHTTPRequestHandler):
    """Pause cold asset requests before nginx resolves its active application."""

    released = threading.Event()
    waiting = 0
    lock = threading.Lock()

    def log_message(self, format, *args):
        """Keep application URLs and diagnostics out of process logs."""

    def do_GET(self):
        """Handle fixture controls or forward an explicitly public asset."""
        cls = type(self)
        if self.path.startswith("/__fixture_gate/"):
            action = self.path.rsplit("/", 1)[-1]
            if action == "hold":
                cls.released.clear()
            elif action == "release":
                cls.released.set()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"waiting": cls.waiting}).encode())
            return
        if not self.path.startswith("/uploads/_frontend-assets/"):
            self.send_error(404)
            return
        with cls.lock:
            cls.waiting += 1
        try:
            if not cls.released.wait(45):
                self.send_error(504)
                return
            connection = http.client.HTTPConnection("proxy", 8081, timeout=10)
            try:
                connection.request("GET", self.path)
                response = connection.getresponse()
                body = response.read()
                self.send_response(response.status)
                for name in ("Content-Type", "Cache-Control", "ETag"):
                    value = response.getheader(name)
                    if value:
                        self.send_header(name, value)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            finally:
                connection.close()
        finally:
            with cls.lock:
                cls.waiting -= 1


def relay_bytes(host, port):
    """Exit on upstream EOF even while the Docker client's stdin remains open."""
    upstream = socket.create_connection((host, port), timeout=5)
    upstream.settimeout(None)

    def send_input():
        try:
            while block := os.read(0, 65536):
                upstream.sendall(block)
            upstream.shutdown(socket.SHUT_WR)
        except OSError:
            os._exit(1)

    threading.Thread(target=send_input, daemon=True).start()
    try:
        while block := upstream.recv(65536):
            remaining = memoryview(block)
            while remaining:
                written = os.write(1, remaining)
                if written <= 0:
                    raise OSError("relay_output_closed")
                remaining = remaining[written:]
    except OSError:
        os._exit(1)
    os._exit(0)


class AssetStack:
    """Own every fixture resource and preserve immutable image identities."""

    def __init__(self, old_image, new_image, output):
        self.images = {"old": old_image, "new": new_image}
        assert all(
            image.startswith("sha256:") and len(image) == 71
            for image in self.images.values()
        )
        self.output, self.prefix = output.resolve(), "otk-assets-" + uuid4().hex[:10]
        self.host = os.environ.get(
            "DOCKER_HOST", "unix://" + str(Path.home() / ".colima/default/docker.sock")
        )
        self.owned, self.relay = [], None
        self.planned = {kind: set() for kind in ("container", "volume", "network")}
        self.network = self.volume = None
        self.active = "old"
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            self.port = listener.getsockname()[1]
        self.url = f"http://127.0.0.1:{self.port}"

    def docker(self, *args):
        """Run a bounded Docker command without printing diagnostics."""
        result = subprocess.run(
            ["docker", "--host", self.host, *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode:
            raise RuntimeError("fixture_docker_failed")
        return result.stdout.strip()

    def request(self, path, method="GET"):
        """Request only this owned loopback fixture."""
        with urlopen(Request(self.url + path, method=method), timeout=12) as response:
            return response.status, response.headers, response.read()

    def wait(self, predicate):
        """Bound readiness polling while observing the same fixture."""
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            try:
                if predicate():
                    return
            except (OSError, http.client.HTTPException):
                pass
            threading.Event().wait(0.1)
        raise TimeoutError("fixture_readiness_timeout")

    def create(self, name, image, arguments, command=()):
        """Create a uniquely named, resource-limited fixture container."""
        self.planned["container"].add(self.prefix + "-" + name)
        memory, cpu = (
            (256, ".6")
            if name in self.images
            else (128, ".4")
            if name == "proxy"
            else (384, ".3")
        )
        cid = self.docker(
            "create",
            "--name",
            self.prefix + "-" + name,
            "--network",
            self.network,
            "--network-alias",
            name,
            "--memory",
            f"{memory}m",
            "--cpus",
            cpu,
            "--pids-limit",
            "96",
            "--log-driver",
            "none",
            "--label",
            "local.otk-assets.owner=" + self.prefix,
            *arguments,
            image,
            *command,
        )
        self.owned.append(cid)
        return cid

    def configuration(self):
        """Configure real caching while keeping HTML and controls uncached."""
        text = f"""events {{}} http {{
          proxy_cache_path /tmp/cache keys_zone=legacy:1m max_size=8m;
          proxy_set_header Host $http_host;
          map $http_upgrade $upgrade_connection {{ default upgrade; '' close; }}
          upstream active {{ server {self.active}:8000; }}
          server {{ listen 8081; location / {{ proxy_pass http://active; }} }}
          server {{ listen 8080;
            add_header X-Fixture-Active {self.active} always;
            location /__fixture_gate/ {{ proxy_pass http://gate:9000; }}
            location /uploads/_frontend-assets/ {{ proxy_pass http://gate:9000; }}
            location ~ ^/(app.js|styles.css)$ {{
              proxy_cache legacy; proxy_cache_valid 200 4h;
              proxy_ignore_headers Cache-Control Expires Set-Cookie;
              add_header X-Fixture-Cache $upstream_cache_status always;
              proxy_pass http://active;
            }}
            location / {{ proxy_pass http://active; proxy_http_version 1.1;
              proxy_set_header Upgrade $http_upgrade;
              proxy_set_header Connection $upgrade_connection;
            }}
          }} }}"""
        (self.output / "nginx.conf").write_text(text)

    def __enter__(self):
        """Prepare actual old/new applications on one synthetic volume."""
        self.output.mkdir(parents=True, exist_ok=True)
        self.before = sorted(self.docker("ps", "-aq", "--no-trunc").split())
        try:
            for kind in ("network", "volume"):
                self.planned[kind].add(self.prefix)
                identity = self.docker(
                    kind,
                    "create",
                    "--label",
                    "local.otk-assets.owner=" + self.prefix,
                    self.prefix,
                )
                setattr(self, kind, identity)
            common = [
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--user",
                "10001:10001",
                "--tmpfs",
                "/tmp:rw,nosuid,nodev,size=32m",
                "--mount",
                f"type=volume,src={self.volume},dst=/data",
                "--env",
                "OTKRYTKA_ENV=test",
                "--env",
                "OTKRYTKA_DB_PATH=/data/fixture.db",
                "--env",
                "OTKRYTKA_UPLOAD_DIR=/data/uploads",
                "--env",
                "OTKRYTKA_FRONTEND_DIR=/app/frontend",
                "--env",
                "OTKRYTKA_CANONICAL_BASE_URL=" + self.url,
                "--health-interval",
                "1s",
                "--health-start-period",
                "1s",
                "--health-timeout",
                "2s",
            ]
            self.apps = {
                name: self.create(name, image, common)
                for name, image in self.images.items()
            }
            self.docker("start", self.apps["old"])
            self.start_proxy_and_gate()
            return self
        except BaseException:
            self.close()
            raise

    def start_proxy_and_gate(self):
        """Start the owned cache, request gate and loopback transport."""
        self.configuration()
        self.proxy = self.create(
            "proxy",
            NGINX,
            ["--mount", f"type=bind,src={self.output},dst=/etc/nginx,readonly"],
        )
        script = Path(__file__).resolve()
        self.gate = self.create(
            "gate",
            self.images["old"],
            [
                "--no-healthcheck",
                "--read-only",
                "--mount",
                f"type=bind,src={script},dst=/gate.py,readonly",
                "--entrypoint",
                "/usr/local/bin/python",
                "--env",
                "PYTHONUNBUFFERED=1",
            ],
            ["/gate.py"],
        )
        self.docker("start", self.gate)
        self.docker("start", self.proxy)
        command = shlex.join(
            ["docker", "--host", self.host, "exec", "-i", self.gate]
            + ["/usr/local/bin/python", "/gate.py", "--relay", "proxy", "8080"]
        )
        self.relay = subprocess.Popen(
            [
                "socat",
                f"TCP-LISTEN:{self.port},bind=127.0.0.1,reuseaddr,fork",
                "EXEC:" + shlex.quote(command),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self.wait(lambda: self.request("/health")[0] == 200)

    def switch(self, name):
        """Switch actual images without replacing their shared data volume."""
        previous = self.active
        self.docker("start", self.apps[name])
        self.wait(
            lambda: (
                self.docker(
                    "inspect", "--format", "{{.State.Health.Status}}", self.apps[name]
                )
                == "healthy"
            )
        )
        self.active = name
        self.configuration()
        self.docker("exec", self.proxy, "nginx", "-s", "reload")
        self.wait(lambda: self.request("/health")[1].get("X-Fixture-Active") == name)
        if previous != name:
            self.docker("stop", "--time", "2", self.apps[previous])

    def labelled_resources(self, kind):
        """Reconcile only planned names carrying this fixture's unique label."""
        command = (
            ("ps", "-a", "--no-trunc")
            if kind == "container"
            else (kind, "ls", "--no-trunc")
            if kind == "network"
            else (kind, "ls")
        )
        template = (
            "{{.ID}}|{{.Names}}"
            if kind == "container"
            else "{{.ID}}|{{.Name}}"
            if kind == "network"
            else "{{.Name}}|{{.Name}}"
        )
        rows = self.docker(
            *command,
            "--filter",
            "label=local.otk-assets.owner=" + self.prefix,
            "--format",
            template,
        )
        records = [row.split("|", 1) for row in rows.splitlines()]
        if any(len(row) != 2 or row[1] not in self.planned[kind] for row in records):
            raise RuntimeError("fixture_unplanned_labelled_resource")
        return [row[0] for row in records]

    def cleanup_attempt(self, phase, operation, failures):
        """Retain safe failure evidence while allowing remaining teardown steps."""
        try:
            return operation()
        except EXPECTED as error:
            failures.append({"phase": phase, "error_class": type(error).__name__})
            return None

    def stop_relay(self, failures):
        """Collect the owned process group even if TERM or wait races its exit."""
        if self.relay and self.relay.poll() is None:
            self.cleanup_attempt(
                "relay_term",
                partial(os.killpg, self.relay.pid, signal.SIGTERM),
                failures,
            )
            if (
                self.cleanup_attempt(
                    "relay_wait", partial(self.relay.wait, timeout=5), failures
                )
                is None
            ):
                self.cleanup_attempt(
                    "relay_kill",
                    partial(os.killpg, self.relay.pid, signal.SIGKILL),
                    failures,
                )
                self.cleanup_attempt(
                    "relay_wait", partial(self.relay.wait, timeout=5), failures
                )

    def close(self):
        """Attempt all owned teardown steps and distinguish foreign additions."""
        failures, remaining = [], {}
        previous = {
            sig: signal.signal(sig, signal.SIG_IGN)
            for sig in (signal.SIGTERM, signal.SIGINT)
        }
        try:
            self.cleanup_attempt("relay", partial(self.stop_relay, failures), failures)
            for kind, known in (
                ("container", self.owned),
                ("volume", [self.volume]),
                ("network", [self.network]),
            ):
                targets = set(filter(None, known))
                targets.update(
                    self.cleanup_attempt(
                        kind + "_discovery",
                        partial(self.labelled_resources, kind),
                        failures,
                    )
                    or []
                )
                command = ("rm", "-f") if kind == "container" else (kind, "rm")
                for target in targets:
                    self.cleanup_attempt(
                        kind + "_remove",
                        partial(self.docker, *command, target),
                        failures,
                    )
            for kind in self.planned:
                remaining[kind] = self.cleanup_attempt(
                    kind + "_remaining",
                    partial(self.labelled_resources, kind),
                    failures,
                )
            after = self.cleanup_attempt(
                "baseline", partial(self.docker, "ps", "-aq", "--no-trunc"), failures
            )
            preserved = after is not None and set(self.before) <= set(after.split())
            absent = all(value == [] for value in remaining.values())
            receipt = {
                "failures": failures,
                "unrelated_containers_preserved": preserved,
                "owned_resources_absent": absent,
            }
            self.cleanup_attempt(
                "receipt",
                partial((self.output / "cleanup.json").write_text, json.dumps(receipt)),
                failures,
            )
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        if failures or not preserved or not absent:
            raise RuntimeError("fixture_cleanup_failed_or_unrelated_drift")

    def __exit__(self, *_args):
        self.close()


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--relay":
        relay_bytes(sys.argv[2], int(sys.argv[3]))
    RequestGate.released.set()
    ThreadingHTTPServer(("0.0.0.0", 9000), RequestGate).serve_forever()
