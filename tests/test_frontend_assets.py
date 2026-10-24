"""Keep release assets consistent across cached navigation and image rollback (#5)."""

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from otkrytka.core.config import get_settings
from otkrytka.core.frontend_assets import build_frontend, publish_frontend_assets
from otkrytka.main import app


@pytest.mark.parametrize(
    "path", ["/", "/index.html", "/unknown-route", "/c/missing", "/embed/missing"]
)
async def test_html_entrypoints_require_revalidation(client, path):
    response = await client.get(path)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache"


def test_build_rewrites_only_copied_html(tmp_path):
    source = Path(__file__).parents[1] / "frontend"
    output = tmp_path / "generated"
    before = (source / "index.html").read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "otkrytka.core.frontend_assets",
            str(source),
            str(output),
        ],
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0
    manifest = json.loads((output / "frontend-assets.json").read_text())
    html = (output / "index.html").read_text()
    for name in ("app.js", "styles.css"):
        data = (source / name).read_bytes()
        assert (output / name).read_bytes() == data
        assert f"/uploads/_frontend-assets/{manifest[name]}" in html
        assert (
            "sha256-" + base64.b64encode(hashlib.sha256(data).digest()).decode() in html
        )
    assert (source / "index.html").read_bytes() == before
    repeated = tmp_path / "repeated"
    build_frontend(source, repeated)
    assert (repeated / "index.html").read_bytes() == (
        output / "index.html"
    ).read_bytes()


@pytest.fixture
def built_frontend(tmp_path):
    source = Path(__file__).parents[1] / "frontend"
    output = tmp_path / "built"
    build_frontend(source, output)
    return output


def test_publication_retains_prior_asset_versions(built_frontend, tmp_path):
    uploads = tmp_path / "uploads"
    publish_frontend_assets(built_frontend, uploads)
    before = {p.name: p.read_bytes() for p in (uploads / "_frontend-assets").iterdir()}
    publish_frontend_assets(built_frontend, uploads)
    source = tmp_path / "source"
    shutil.copytree(Path(__file__).parents[1] / "frontend", source)
    data = (source / "app.js").read_bytes()
    (source / "app.js").write_bytes(data.replace(b"const", b"let  ", 1))
    newer = tmp_path / "newer"
    build_frontend(source, newer)
    publish_frontend_assets(newer, uploads)
    assert all(
        (uploads / "_frontend-assets" / name).read_bytes() == data
        for name, data in before.items()
    )
    assert len(list((uploads / "_frontend-assets").glob("*.js"))) == 2
    assert len(list((uploads / "_frontend-assets").glob("*.css"))) == 1


@pytest.mark.parametrize(
    "conflict", ["bytes", "symlink", "directory", "manifest", "source"]
)
def test_corrupt_resources_fail_without_overwrite(built_frontend, tmp_path, conflict):
    uploads = tmp_path / "uploads"
    directory = uploads / "_frontend-assets"
    directory.mkdir(parents=True)
    manifest = json.loads((built_frontend / "frontend-assets.json").read_text())
    destination = directory / manifest["app.js"]
    if conflict == "bytes":
        destination.write_bytes(b"corrupt")
    elif conflict == "symlink":
        destination.symlink_to(built_frontend / "app.js")
    elif conflict == "directory":
        directory.rmdir()
        directory.symlink_to(
            built_frontend / "_frontend-assets", target_is_directory=True
        )
    elif conflict == "manifest":
        (built_frontend / "frontend-assets.json").write_text('{"app.js":"../escape"}')
    else:
        (built_frontend / "_frontend-assets" / manifest["app.js"]).write_bytes(
            b"corrupt"
        )
    with pytest.raises((ValueError, OSError)):
        publish_frontend_assets(built_frontend, uploads)
    if conflict == "bytes":
        assert destination.read_bytes() == b"corrupt"
    assert not (tmp_path / "escape").exists()


def test_failed_write_never_exposes_digest_filename(
    built_frontend, tmp_path, monkeypatch
):
    uploads = tmp_path / "uploads"

    def fail_sync(_descriptor):
        raise OSError("injected filesystem failure")

    monkeypatch.setattr(os, "fsync", fail_sync)
    with pytest.raises(OSError, match="injected"):
        publish_frontend_assets(built_frontend, uploads)
    assert list((uploads / "_frontend-assets").iterdir()) == []


def test_concurrent_publishers_expose_only_complete_assets(built_frontend, tmp_path):
    uploads = tmp_path / "uploads"
    barrier = threading.Barrier(4)
    stop = threading.Event()
    observed = threading.Event()
    started = threading.Event()

    def observe():
        started.set()
        while not stop.is_set():
            for path in uploads.glob("_frontend-assets/[!.]*"):
                assert hashlib.sha256(path.read_bytes()).hexdigest() == path.stem
                observed.set()

    def publish():
        barrier.wait(timeout=5)
        publish_frontend_assets(built_frontend, uploads)

    with ThreadPoolExecutor(max_workers=5) as executor:
        reader = executor.submit(observe)
        assert started.wait(timeout=5)
        try:
            futures = [executor.submit(publish) for _ in range(4)]
            for future in futures:
                future.result(timeout=10)
            assert observed.wait(timeout=5)
        finally:
            stop.set()
        reader.result(timeout=5)
    directory = uploads / "_frontend-assets"
    assert len(list(directory.iterdir())) == 2
    for path in directory.iterdir():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == path.stem
        assert path.stat().st_mode & 0o222 == 0


@pytest.fixture
async def generated_site(client, built_frontend, tmp_path, monkeypatch):
    settings = get_settings()
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(settings, "frontend_dir", str(built_frontend))
    monkeypatch.setattr(settings, "upload_dir", str(uploads))
    for route in app.routes:
        if isinstance(route, Mount) and route.name in ("frontend", "uploads"):
            directory = built_frontend if route.name == "frontend" else uploads
            monkeypatch.setattr(route.app, "directory", str(directory))
            monkeypatch.setattr(route.app, "all_directories", [str(directory)])
    async with app.router.lifespan_context(app):
        yield client, built_frontend, uploads


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/index.html",
        "/unknown-route",
        "/c/missing",
        "/embed/missing",
        "/c/{slug}",
        "/embed/{slug}",
    ],
)
async def test_generated_html_and_delayed_old_static_fetch(generated_site, path):
    client, frontend, uploads = generated_site
    created = (
        await client.post("/api/v1/boards", json={"title": "Asset fixture"})
    ).json()
    path = path.replace("{slug}", created["slug"])
    response = await client.get(path)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache"
    manifest = json.loads((frontend / "frontend-assets.json").read_text())
    async with AsyncClient(
        transport=ASGITransport(app=StaticFiles(directory=uploads)),
        base_url="http://old",
    ) as old:
        for name, filename in manifest.items():
            url = "/uploads/_frontend-assets/" + filename
            assert url in response.text
            body = await client.get(url)
            delayed = await old.get("/_frontend-assets/" + filename)
            assert body.content == delayed.content == (frontend / name).read_bytes()
            assert (
                body.headers["cache-control"] == "public, max-age=31536000, immutable"
            )
            mime = delayed.headers["content-type"]
            assert (
                "javascript" in mime
                if name.endswith(".js")
                else mime.startswith("text/css")
            )
            assert (
                "sha256-"
                + base64.b64encode(hashlib.sha256(body.content).digest()).decode()
                in response.text
            )
    assert (
        await client.get("/uploads/_frontend-assets/" + "0" * 64 + ".js")
    ).status_code == 404


async def test_image_api_cannot_target_retained_code(generated_site):
    client, frontend, uploads = generated_site
    created = (
        await client.post("/api/v1/boards", json={"title": "Asset fixture"})
    ).json()
    slug = created["slug"]
    filename = json.loads((frontend / "frontend-assets.json").read_text())["app.js"]
    path = uploads / "_frontend-assets" / filename
    before = path.read_bytes()
    response = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": (filename, b"alert('x')", "application/javascript")},
    )
    assert response.status_code == 415
    response = await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={
            "author_name": "Fixture",
            "image_path": "/uploads/_frontend-assets/" + filename,
        },
    )
    assert response.status_code == 400
    board = (await client.get(f"/api/v1/boards/{slug}")).json()
    response = await client.request(
        "DELETE",
        f"/api/v1/boards/{board['id']}",
        json={"organizer_token": created["organizer_token"]},
    )
    assert response.status_code == 204
    assert path.read_bytes() == before


def test_source_development_skips_only_absent_manifest(tmp_path):
    source = Path(__file__).parents[1] / "frontend"
    publish_frontend_assets(source, tmp_path / "uploads", development=True)
    assert not (tmp_path / "uploads").exists()
    with pytest.raises(ValueError, match="frontend_manifest_missing"):
        publish_frontend_assets(source, tmp_path / "uploads")


async def test_invalid_manifest_blocks_startup(built_frontend, tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "frontend_dir", str(built_frontend))
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "uploads"))
    (built_frontend / "frontend-assets.json").write_text("{}")
    with pytest.raises(ValueError, match="frontend_manifest_invalid"):
        async with app.router.lifespan_context(app):
            pytest.fail("Invalid assets must prevent readiness")
