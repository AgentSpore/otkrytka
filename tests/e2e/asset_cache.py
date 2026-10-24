"""Exercise issue #5 with real images, nginx cache and a cache-enabled browser.

Run separately from application pytest with
``uv run --with playwright python tests/e2e/asset_cache.py`` and immutable
--old-image/--new-image values after building both revisions.
"""

import argparse
import base64
import hashlib
import json
from datetime import UTC, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from asset_cache_stack import AssetStack, fixture_signals
from playwright.sync_api import expect, sync_playwright


class AssetReferences(HTMLParser):
    """Read only the generated first-party references from real HTML."""

    def __init__(self, document):
        super().__init__()
        self.assets = {}
        self.feed(document.decode())

    def handle_starttag(self, tag, attrs: list[tuple[str, str | None]]):
        values = dict(attrs)
        path = values.get("src", values.get("href", "")) or ""
        if path.startswith("/uploads/_frontend-assets/"):
            self.assets[path] = values.get("integrity")


class AssetCacheProbe:
    """Verify observable browser bytes and retain sanitized release artifacts."""

    def __init__(self, stack):
        self.stack, self.errors, self.assets = stack, [], {}
        self.report: dict[str, object] = {
            "tls_verified": False,
            "transport": "owned socat loopback relay",
            "browser_cache_disabled": False,
        }

    def observe(self, page):
        """Fail browser faults without recording tokens, URLs or error prose."""
        page.on("pageerror", lambda _error: self.errors.append("pageerror"))
        page.on(
            "console",
            lambda item: (
                self.errors.append("console_error") if item.type == "error" else None
            ),
        )
        page.on("requestfailed", lambda _request: self.errors.append("requestfailed"))
        page.on(
            "response",
            lambda item: (
                self.errors.append("same_origin_http_" + str(item.status))
                if item.url.startswith(self.stack.url) and item.status >= 400
                else None
            ),
        )

    def read_assets(self, path):
        """Assert generated HTML references exact hashes and SRI values."""
        status, headers, document = self.stack.request(path)
        assert status == 200 and headers.get("Cache-Control") in {
            "no-cache",
            "no-store",
        }
        assets = AssetReferences(document).assets
        assert len(assets) == 2, "generated_asset_references_missing"
        for filename, integrity in assets.items():
            digest = Path(filename).stem
            assert (
                len(digest) == 64
                and integrity
                == "sha256-" + base64.b64encode(bytes.fromhex(digest)).decode()
            )
        return assets

    def collect_asset_response(self, response, completed):
        """Retain only first-party generated asset responses, never private URLs."""
        path = urlsplit(response.url).path
        if response.url.startswith(self.stack.url + "/") and path in self.assets:
            completed[path] = response

    def verify_browser_assets(self, page, completed):
        """Prove both actual browser byte streams crossed the network after rollback."""
        assert set(completed) == set(self.assets), "browser_asset_response_missing"
        transfers = page.evaluate(
            """paths => Object.fromEntries(performance.getEntriesByType('resource')
              .filter(entry => new URL(entry.name).origin === location.origin &&
                paths.includes(new URL(entry.name).pathname))
              .map(entry => [new URL(entry.name).pathname, entry.transferSize]))""",
            list(self.assets),
        )
        observed = {}
        for path, response in completed.items():
            digest = hashlib.sha256(response.body()).hexdigest()
            mime = response.headers.get("content-type", "")
            assert response.status == 200 and digest == Path(path).stem
            assert ("javascript" if path.endswith(".js") else "text/css") in mime
            assert transfers.get(path, 0) > 0, "browser_asset_not_network_transfer"
            observed[path] = {
                "sha256": digest,
                "mime": mime,
                "transfer_size": transfers[path],
            }
        self.report["browser_cold_assets_after_rollback"] = observed

    def delayed_rollback(self, browser):
        """Hold cold requests at the proxy, then serve them from the old image."""
        with browser.new_context(service_workers="block") as context:
            page = context.new_page()
            self.observe(page)
            page.goto(self.stack.url, wait_until="domcontentloaded")
            expect(page.locator("#create-title")).to_be_visible()
            self.stack.switch("new")
            self.assets = self.read_assets("/")
            completed = {}
            page.on(
                "response",
                lambda response: self.collect_asset_response(response, completed),
            )
            self.stack.request("/__fixture_gate/hold")
            page.reload(wait_until="commit")
            self.stack.wait(
                lambda: (
                    json.loads(self.stack.request("/__fixture_gate/state")[2])[
                        "waiting"
                    ]
                    >= 1
                )
            )
            assert page.evaluate("document.readyState") == "loading"
            assert not completed, "browser_asset_completed_before_rollback"
            self.stack.switch("old")
            self.stack.request("/__fixture_gate/release")
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.verify_browser_assets(page, completed)
            expect(page.locator("#create-title")).to_be_visible(timeout=15000)
            observed = {}
            for path, integrity in self.assets.items():
                status, headers, data = self.stack.request(path)
                assert (
                    status == 200
                    and hashlib.sha256(data).hexdigest() == Path(path).stem
                )
                assert (
                    "javascript" if path.endswith(".js") else "text/css"
                ) in headers.get("Content-Type", "")
                observed[path] = {
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                    "integrity": integrity,
                }
            assert not self.errors
            self.report["delayed_rollback"] = observed

    def organizer(self, browser):
        """Create a synthetic board and close private link UI before capture."""
        context = browser.new_context(
            service_workers="block", viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()
        self.observe(page)
        page.goto(self.stack.url, wait_until="domcontentloaded")
        page.locator("#create-title").fill("Synthetic asset rollout")
        page.locator("#create-reveal").fill(
            (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        )
        page.locator("#create-btn").click()
        guest = urlsplit(page.locator('[data-field="share"]').input_value()).path
        page.locator('[data-f="ack"]').check()
        page.locator('[data-action="go"]').click()
        expect(page.locator('[data-field="manage"]')).to_have_count(0)
        page.wait_for_function(
            "typeof ws !== 'undefined' && ws.socket?.readyState === WebSocket.OPEN"
        )
        return context, page, guest

    def views(self, browser):
        """Verify all HTML sources, real guest changes and both viewport artifacts."""
        self.stack.switch("new")
        owner, page, guest = self.organizer(browser)
        try:
            routes = (
                "/",
                "/index.html",
                "/asset-fixture-unknown",
                guest,
                "/embed/" + guest.rsplit("/", 1)[-1],
            )
            for path in routes:
                assert self.read_assets(path) == self.assets
            with browser.new_context(
                service_workers="block",
                viewport={"width": 390, "height": 844},
                record_video_dir=self.stack.output / "video",
            ) as context:
                visitor = context.new_page()
                self.observe(visitor)
                visitor.goto(self.stack.url + guest, wait_until="domcontentloaded")
                visitor.locator("#add-wish-btn").click()
                visitor.locator('[data-f="name"]').fill("Synthetic guest")
                visitor.locator('[data-f="text"]').fill(
                    "Retained assets and live updates"
                )
                visitor.locator('[data-f="send"]').click()
                expect(
                    page.get_by_text("Retained assets and live updates", exact=True)
                ).to_be_visible()
                visitor.reload(wait_until="domcontentloaded")
                visitor.wait_for_function(
                    "typeof ws !== 'undefined' && ws.socket?.readyState === WebSocket.OPEN"
                )
                expect(visitor.locator("#add-wish-btn")).to_be_visible()
                assert visitor.evaluate(
                    "document.documentElement.scrollWidth <= innerWidth"
                )
                visitor.screenshot(path=self.stack.output / "guest-390.png")
            page.screenshot(path=self.stack.output / "organizer-1440.png")
            page.reload(wait_until="domcontentloaded")
            page.wait_for_function(
                "typeof ws !== 'undefined' && ws.socket?.readyState === WebSocket.OPEN"
            )
            assert not self.errors
            self.report["html_entrypoints"] = list(routes)
        finally:
            owner.close()

    def run(self, browser):
        """Prove a warmed legacy cache cannot substitute for generated assets."""
        legacy = {}
        for path in ("/app.js", "/styles.css"):
            first = self.stack.request(path)
            second = self.stack.request(path)
            assert first[2] == second[2] and second[1].get("X-Fixture-Cache") == "HIT"
            legacy[path] = {
                "sha256": hashlib.sha256(second[2]).hexdigest(),
                "bytes": len(second[2]),
                "cache_status": "HIT",
            }
        self.report["legacy_cache"] = legacy
        (self.stack.output / "legacy-cache.json").write_text(json.dumps(legacy))
        self.delayed_rollback(browser)
        self.views(browser)
        self.stack.switch("old")
        assert self.stack.request("/health")[0] == 200
        self.report.update(
            passed=True, browser_errors=self.errors, images=self.stack.images
        )
        (self.stack.output / "browser-proof.json").write_text(
            json.dumps(self.report, indent=2) + "\n"
        )


def main(options):
    """Emit only safe failure metadata after fixture contexts have unwound."""
    phase = "fixture"
    try:
        with (
            fixture_signals(),
            AssetStack(options.old_image, options.new_image, options.output) as fixture,
            sync_playwright() as engine,
        ):
            phase = "browser"
            with engine.chromium.launch(
                executable_path=options.browser, headless=True
            ) as chromium:
                phase = "scenario"
                AssetCacheProbe(fixture).run(chromium)
    except (Exception, KeyboardInterrupt) as error:
        print(
            json.dumps(
                {"passed": False, "phase": phase, "error_class": type(error).__name__}
            )
        )
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-image", required=True)
    parser.add_argument("--new-image", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--browser",
        default="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )
    options = parser.parse_args()
    raise SystemExit(main(options))
