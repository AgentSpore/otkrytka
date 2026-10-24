"""Build and retain public frontend artifacts across application image rollback."""

import argparse
import base64
import hashlib
import json
import os
import secrets
import shutil
import stat
from pathlib import Path

ASSET_NAMES = ("app.js", "styles.css")
ASSET_PREFIX = "/uploads/_frontend-assets/"
MANIFEST_NAME = "frontend-assets.json"
HTML_CACHE_CONTROL = "no-cache"
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"


def _read_regular(
    path: Path | str, directory_fd: int | None = None, expected_size: int | None = None
) -> bytes:
    with os.fdopen(
        os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd),
        "rb",
    ) as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError("frontend_asset_not_regular")
        if (
            expected_size is not None
            and os.fstat(source.fileno()).st_size != expected_size
        ):
            raise ValueError("frontend_asset_conflict")
        return source.read()


def _asset_filename(name: str, data: bytes) -> str:
    return hashlib.sha256(data).hexdigest() + Path(name).suffix


def build_frontend(source: Path, output: Path) -> None:
    """Copy the frontend and fingerprint its fixed first-party JS/CSS references."""
    html = _read_regular(source / "index.html").decode("utf-8")
    shutil.copytree(source, output)
    assets = output / "_frontend-assets"
    assets.mkdir()
    manifest = {}
    for name in ASSET_NAMES:
        data = _read_regular(source / name)
        filename = _asset_filename(name, data)
        attribute = "src" if name.endswith(".js") else "href"
        reference = f'{attribute}="/{name}"'
        if html.count(reference) != 1:
            raise ValueError("frontend_asset_reference_invalid")
        integrity = base64.b64encode(bytes.fromhex(Path(filename).stem)).decode("ascii")
        html = html.replace(
            reference,
            f'{attribute}="{ASSET_PREFIX}{filename}" integrity="sha256-{integrity}"',
        )
        (assets / filename).write_bytes(data)
        manifest[name] = filename
    (output / "index.html").write_text(html, encoding="utf-8")
    (output / MANIFEST_NAME).write_text(
        json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8"
    )


def _publish_file(directory_fd: int, filename: str, data: bytes) -> None:
    temporary = ".publish-" + secrets.token_hex(16)
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=directory_fd,
    )
    try:
        with os.fdopen(descriptor, "wb") as target:
            target.write(data)
            target.flush()
            os.fchmod(target.fileno(), 0o444)
            os.fsync(target.fileno())
        # INVARIANT(AS5): final digest names become visible only after complete writes.
        try:
            os.link(
                temporary,
                filename,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
        except FileExistsError:
            if _read_regular(filename, directory_fd, len(data)) != data:
                raise ValueError("frontend_asset_conflict") from None
        os.fsync(directory_fd)
    finally:
        os.unlink(temporary, dir_fd=directory_fd)


def publish_frontend_assets(
    frontend: Path, uploads: Path, development: bool = False
) -> None:
    """Publish verified image artifacts before readiness, retaining earlier versions."""
    manifest_path = frontend / MANIFEST_NAME
    if not manifest_path.exists() and not manifest_path.is_symlink():
        if development and ASSET_PREFIX not in _read_regular(
            frontend / "index.html"
        ).decode("utf-8"):
            return
        raise ValueError("frontend_manifest_missing")
    manifest = json.loads(_read_regular(manifest_path))
    if not isinstance(manifest, dict) or set(manifest) != set(ASSET_NAMES):
        raise ValueError("frontend_manifest_invalid")
    entries = []
    for name in ASSET_NAMES:
        filename = manifest[name]
        if (
            not isinstance(filename, str)
            or len(filename) != 64 + len(Path(name).suffix)
            or not all(c in "0123456789abcdef" for c in filename[:64])
            or filename[64:] != Path(name).suffix
        ):
            raise ValueError("frontend_manifest_invalid")
        data = _read_regular(frontend / "_frontend-assets" / filename)
        if filename != _asset_filename(name, data):
            raise ValueError("frontend_asset_hash_invalid")
        entries.append((filename, data))
    uploads.mkdir(parents=True, exist_ok=True)
    directory = uploads / "_frontend-assets"
    directory.mkdir(mode=0o755, exist_ok=True)
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for filename, data in entries:
            _publish_file(descriptor, filename, data)
    finally:
        os.close(descriptor)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    build_frontend(arguments.source, arguments.output)
