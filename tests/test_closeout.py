"""Close-out regressions:

  1. Fail-closed canonical origin in production (Settings validator).
  2. Versioned libraries are vendored same-origin (no jsdelivr) and served by the
     static mount; index.html CSP no longer allows cdn.jsdelivr.net.
  3. Honest delete copy (no promise of permanent/legal erasure).
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from otkrytka.core.config import Settings, get_settings


# --- 1. canonical fail-closed in production ------------------------------------

def test_prod_env_without_canonical_fails_at_startup():
    with pytest.raises(ValidationError):
        Settings(env="production", canonical_base_url="")


def test_prod_env_with_canonical_ok():
    s = Settings(env="production", canonical_base_url="https://otkrytka.agentspore.com")
    assert s.canonical_base_url == "https://otkrytka.agentspore.com"


@pytest.mark.parametrize("env", ["dev", "local", "test", "DEV", " Test "])
def test_non_prod_env_without_canonical_ok(env):
    s = Settings(env=env, canonical_base_url="")
    assert s.canonical_base_url == ""


def test_prod_env_with_blank_canonical_fails():
    with pytest.raises(ValidationError):
        Settings(env="staging", canonical_base_url="   ")


# --- 2. vendored libs, no jsdelivr ---------------------------------------------

def _frontend_dir() -> Path:
    return Path(get_settings().frontend_dir)


def test_vendor_files_exist_and_non_empty():
    vendor = _frontend_dir() / "vendor"
    for name in ("confetti.browser.min.js", "qrcode.min.js"):
        f = vendor / name
        assert f.is_file(), f"missing vendored lib {name}"
        assert f.stat().st_size > 1000, f"vendored lib {name} looks empty"


def test_index_html_uses_local_vendor_not_jsdelivr():
    html = (_frontend_dir() / "index.html").read_text(encoding="utf-8")
    assert "cdn.jsdelivr.net" not in html
    assert "/vendor/confetti.browser.min.js" in html
    assert "/vendor/qrcode.min.js" in html


def test_csp_drops_jsdelivr_keeps_self_and_tailwind():
    html = (_frontend_dir() / "index.html").read_text(encoding="utf-8")
    csp_line = next(
        line for line in html.splitlines()
        if 'http-equiv="Content-Security-Policy"' in line
    )
    assert "cdn.jsdelivr.net" not in csp_line
    assert "'self'" in csp_line
    assert "cdn.tailwindcss.com" in csp_line


@pytest.mark.asyncio
async def test_static_mount_serves_vendor(client):
    for name in ("confetti.browser.min.js", "qrcode.min.js"):
        r = await client.get(f"/vendor/{name}")
        assert r.status_code == 200, name
        assert len(r.content) > 1000


# --- 3. honest delete copy -----------------------------------------------------

def test_delete_copy_is_honest():
    app_js = (_frontend_dir() / "app.js").read_text(encoding="utf-8")
    # No promise of permanent / forever / irreversible legal erasure.
    for bad in ("permanently", "forever", "навсегда", "безвозвратно"):
        assert bad.lower() not in app_js.lower(), f"delete copy over-promises: {bad}"
    # Board delete copy names the reversible/hide semantics (en+ru).
    assert "Hide this card from everyone" in app_js
    assert "Скрыть открытку от всех" in app_js
