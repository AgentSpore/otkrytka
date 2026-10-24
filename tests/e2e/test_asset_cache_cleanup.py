"""Guard fixture ownership and teardown at real subprocess boundaries."""

import json
import os
import select
import shlex
import signal
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

import asset_cache_stack as stack_module
from asset_cache_stack import AssetStack


@pytest.fixture
def fixture_stack(tmp_path, monkeypatch):
    stack = AssetStack("sha256:" + "0" * 64, "sha256:" + "1" * 64, tmp_path)
    stack.owned, stack.network, stack.volume = ["one", "two"], "network", "volume"
    stack.before = ["baseline"]
    calls = []

    def boundary(args, **_kwargs):
        command = args[3:]
        calls.append(command)
        text = (
            "baseline\nforeign-added"
            if command[0] == "ps" and "--format" not in command
            else ""
        )
        if command[0] == "create":
            text = ("a" if "proxy" in command else "b") * 64
        return subprocess.CompletedProcess(args, 0, text, "")

    monkeypatch.setattr(stack_module.subprocess, "run", boundary)
    return stack, calls, boundary


@pytest.mark.parametrize(
    "failure", [subprocess.TimeoutExpired("docker", 1), OSError("synthetic")]
)
def test_removal_failure_still_attempts_every_owned_resource(
    fixture_stack, monkeypatch, failure
):
    stack, calls, boundary = fixture_stack

    def fail_first(args, **kwargs):
        if args[3:6] == ["rm", "-f", "two"]:
            calls.append(args[3:])
            raise failure
        return boundary(args, **kwargs)

    monkeypatch.setattr(stack_module.subprocess, "run", fail_first)
    with pytest.raises(RuntimeError):
        stack.close()
    assert ["rm", "-f", "one"] in calls
    assert ["volume", "rm", "volume"] in calls and ["network", "rm", "network"] in calls
    assert json.loads((stack.output / "cleanup.json").read_text())["failures"]


def test_exited_relay_race_does_not_skip_docker_cleanup(fixture_stack, monkeypatch):
    stack, calls, _ = fixture_stack
    stack.relay = SimpleNamespace(pid=123, poll=lambda: None, wait=lambda **_: 0)

    def vanished(*_args):
        raise ProcessLookupError("synthetic")

    monkeypatch.setattr(stack_module.os, "killpg", vanished)
    with pytest.raises(RuntimeError):
        stack.close()
    assert ["rm", "-f", "one"] in calls and ["rm", "-f", "two"] in calls
    assert ["volume", "rm", "volume"] in calls and ["network", "rm", "network"] in calls


def test_foreign_addition_preserves_baseline_without_false_failure(fixture_stack):
    stack, _, _ = fixture_stack
    stack.close()
    assert json.loads((stack.output / "cleanup.json").read_text())[
        "unrelated_containers_preserved"
    ]


@pytest.mark.parametrize("kind", ["network", "volume", "container"])
def test_lost_create_ack_is_reconciled_only_with_own_label(tmp_path, monkeypatch, kind):
    stack = AssetStack("sha256:" + "0" * 64, "sha256:" + "1" * 64, tmp_path)
    created, removed = {}, []

    def boundary(args, **_kwargs):
        command, text = args[3:], ""
        current = "container" if command[0] in {"create", "ps", "rm"} else command[0]
        if "create" in command:
            name = (
                command[command.index("--name") + 1]
                if current == "container"
                else command[-1]
            )
            label = (
                command[command.index("--label") + 1] if "--label" in command else ""
            )
            created[current] = (name, label)
            if current == kind:
                raise subprocess.TimeoutExpired("docker", 1)
            text = name
        elif "--format" in command and current in created:
            name, label = created[current]
            if label == "local.otk-assets.owner=" + stack.prefix:
                text = name + "|" + name
        elif "rm" in command:
            removed.append((current, command[-1]))
            created.pop(current, None)
        return subprocess.CompletedProcess(args, 0, text, "")

    monkeypatch.setattr(stack_module.subprocess, "run", boundary)
    with pytest.raises((RuntimeError, subprocess.TimeoutExpired)):
        stack.__enter__()
    assert kind not in created, "lost_ack_resource_leaked"
    assert any(name.startswith(stack.prefix) for _, name in removed)


CANCELLATION = """
import json,runpy,signal,subprocess,sys,types
from pathlib import Path
from unittest.mock import patch,MagicMock
sys.path.insert(0,sys.argv[1])
import asset_cache_stack as module
output=Path(sys.argv[2]);mode=sys.argv[3];calls=[]
def boundary(args,**kwargs):
 command=args[3:];calls.append(command)
 text=(command[command.index('--name')+1] if command[0]=='create'
       else command[-1] if 'create' in command else '')
 return subprocess.CompletedProcess(args,0,text,'')
class BrowserBoundary:
 def __enter__(self):
  print('fixture_ready',flush=True)
  if mode=='private':raise RuntimeError('synthetic organizer_token=PRIVATE')
  signal.pause()
 def __exit__(self,*args):pass
api=types.ModuleType('playwright.sync_api')
api.expect=lambda *args:None;api.sync_playwright=BrowserBoundary
sys.modules['playwright']=types.ModuleType('playwright');sys.modules['playwright.sync_api']=api
response=MagicMock(status=200,headers={});response.__enter__.return_value=response;response.read.return_value=b''
relay=types.SimpleNamespace(pid=1,poll=lambda:0)
sys.argv=['asset_cache.py','--old-image','sha256:'+'0'*64,'--new-image','sha256:'+'1'*64,'--output',str(output)]
with (patch.object(module.subprocess,'run',boundary),
      patch.object(module.subprocess,'Popen',return_value=relay),
      patch.object(module,'urlopen',return_value=response)):
 try:runpy.run_path(str(Path(sys.path[0])/'asset_cache.py'),run_name='__main__')
 except (RuntimeError,SystemExit):pass
(output/'cancellation-calls.json').write_text(json.dumps(calls))
"""


@pytest.mark.parametrize("mode", ["term", "private"])
def test_actual_entrypoint_failure_unwinds_and_sanitizes(tmp_path, mode):
    command = [
        sys.executable,
        "-c",
        CANCELLATION,
        str(Path(__file__).parent),
        str(tmp_path),
        mode,
    ]
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    ) as process:
        assert process.stdout is not None
        try:
            assert select.select([process.stdout], [], [], 5)[0]
            assert process.stdout.readline().strip() == "fixture_ready"
            if mode == "term":
                os.kill(process.pid, signal.SIGTERM)
            assert process.wait(timeout=5) == 0
            failure = json.loads(process.stdout.read())
            assert failure["passed"] is False and "PRIVATE" not in json.dumps(failure)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
    calls = json.loads((tmp_path / "cancellation-calls.json").read_text())
    assert sum(command[:2] == ["rm", "-f"] for command in calls) == 4
    assert any(command[:2] == ["volume", "rm"] for command in calls)
    assert any(command[:2] == ["network", "rm"] for command in calls)


def test_nginx_starts_after_gate_dependency(tmp_path, monkeypatch):
    stack = AssetStack("sha256:" + "0" * 64, "sha256:" + "1" * 64, tmp_path)
    gate_started = False

    def boundary(args, **_kwargs):
        nonlocal gate_started
        command = args[3:]
        if command[0] == "start":
            if command[-1].endswith("-gate"):
                gate_started = True
            else:
                assert gate_started, "nginx_host_not_found"
                raise OSError("stop_after_dependency_ready")
        name = command[command.index("--name") + 1] if "--name" in command else ""
        return subprocess.CompletedProcess(args, 0, name, "")

    monkeypatch.setattr(stack_module.subprocess, "run", boundary)
    with pytest.raises(OSError, match="stop_after_dependency_ready"):
        stack.start_proxy_and_gate()


def test_http_header_lookup_is_case_insensitive(tmp_path):
    class LowercaseHeaders(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("cache-control", "no-cache")
            self.end_headers()
            self.wfile.write(b"ok")

    server = ThreadingHTTPServer(("127.0.0.1", 0), LowercaseHeaders)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        stack = AssetStack("sha256:" + "0" * 64, "sha256:" + "1" * 64, tmp_path)
        stack.url = "http://127.0.0.1:" + str(server.server_port)
        status, headers, body = stack.request("/")
        assert (status, headers.get("Cache-Control"), body) == (200, "no-cache", b"ok")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_socat_exec_preserves_uri_and_docker_argv(fixture_stack, monkeypatch):
    stack, calls, _ = fixture_stack

    def relay(args, **_kwargs):
        gate = next(
            call
            for call in calls
            if call[0] == "create" and call[call.index("--name") + 1].endswith("-gate")
        )
        assert gate[gate.index("--memory") + 1] == "384m"
        assert gate[gate.index("--cpus") + 1] == ".3"
        assert "--no-healthcheck" in gate
        command = shlex.split(args[-1].removeprefix("EXEC:"))
        assert len(command) == 1, "socat_exec_address_split"
        argv = shlex.split(command[0])
        assert argv[:3] == ["docker", "--host", stack.host]
        assert argv[3:6] == ["exec", "-i", stack.gate]
        assert argv[6:] == [
            "/usr/local/bin/python",
            "/gate.py",
            "--relay",
            "proxy",
            "8080",
        ]
        raise OSError("stop_after_valid_exec_address")

    monkeypatch.setattr(stack_module.subprocess, "Popen", relay)
    with pytest.raises(OSError, match="stop_after_valid_exec_address"):
        stack.start_proxy_and_gate()


def relay_command(listener, broken_stdin):
    """Launch the actual helper with real pipe or unreadable input FD."""
    command = [
        sys.executable,
        str(Path(stack_module.__file__).resolve()),
        "--relay",
        "127.0.0.1",
        str(listener.getsockname()[1]),
    ]
    if broken_stdin:
        command = [
            sys.executable,
            "-c",
            "import os,runpy,sys;os.dup2(os.open(os.devnull,os.O_WRONLY),0);sys.argv=sys.argv[1:];"
            "runpy.run_path(sys.argv[0],run_name='__main__')",
            *command[1:],
        ]
    return command


@pytest.mark.parametrize("broken_stdin", [False, True])
def test_real_inner_relay_preserves_binary_stream_and_exits_on_eof(broken_stdin):
    payload = bytes(range(256)) * 1024
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.settimeout(3)
    command = relay_command(listener, broken_stdin)
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0,
    )
    try:
        peer, _ = listener.accept()
        with peer:
            peer.settimeout(3)
            assert process.stdin is not None and process.stdout is not None
            if broken_stdin:
                assert process.wait(timeout=3) != 0
                assert peer.recv(1) == b""
            else:
                for message in (b"keepalive", payload):
                    sender = threading.Thread(target=peer.sendall, args=(message,))
                    sender.start()
                    observed = bytearray()
                    while len(observed) < len(message):
                        assert select.select([process.stdout], [], [], 3)[0]
                        block = os.read(
                            process.stdout.fileno(), len(message) - len(observed)
                        )
                        assert block, "premature_relay_eof"
                        observed.extend(block)
                    sender.join(timeout=3)
                    assert not sender.is_alive() and observed == message
                    process.stdin.write(b"ack")
                    assert peer.recv(3) == b"ack"
                    assert process.poll() is None
                peer.shutdown(socket.SHUT_WR)
                assert process.wait(timeout=3) == 0
                assert not process.stdin.closed, "upstream_eof_requires_open_stdin"
                assert process.stdout.read() == b""
    finally:
        listener.close()
        if process.poll() is None:
            process.kill()
        process.wait(timeout=3)
        if process.stdin:
            process.stdin.close()
        if process.stdout:
            process.stdout.close()
