"""Real Chrome router component regression; renderers/WS are counted boundaries."""

import argparse
import asyncio
import hashlib
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ORIGIN = "http://127.0.0.1:19473"


def extract_router(source):
    """Fail closed if the production routing or initialization seam changes."""
    routing = re.search(
        r"// ─── Routing ─[^\n]*\n(.*?)// ═+\n// SCREEN 1 — Landing", source, re.DOTALL
    )
    initialization = re.search(
        r"// ─── Init ─[^\n]*\n(function init\(\) \{.*?\n\}\n\ninit\(\);)\s*$",
        source,
        re.DOTALL,
    )
    assert routing and initialization, "production router/init extraction mismatch"
    for name in ("parseRoute", "goTo", "goHome", "render"):
        assert len(re.findall(rf"\bfunction {name}\(", routing[1])) == 1, name
    assert "addEventListener('hashchange', rerender)" in initialization[1]
    assert "addEventListener('popstate', rerender)" in initialization[1]
    return routing[1] + initialization[1]


BOUNDARIES = """
const state = {lang: 'en', board: null};
const counts = {renders: 0, closes: 0, boards: 0, adopted: 0};
const events = [];
const errors = [];
window.addEventListener('error', e => errors.push(e.message));
for (const name of ['popstate', 'hashchange']) {
  window.addEventListener(name, () => events.push(name));
}
function t(key) { return key; }
function clearAllModals() {}
function wsClose() { counts.closes++; }
function setOrgToken() { counts.adopted++; }
function renderLanding() { counts.renders++; }
function renderNotFound() { counts.renders++; }
function renderDeliver() { counts.renders++; }
function renderEmbed() { counts.renders++; }
function renderBoard() { counts.renders++; counts.boards++; }
"""


async def transition(
    page, action, expected_renders, event="hashchange", expected_closes=None
):
    """Wait for the browser event, then assert the completed route dispatch count."""
    before = await page.evaluate("({...counts})")
    await page.evaluate(
        """({action, event}) => new Promise(resolve => {
          window.addEventListener(event, () => requestAnimationFrame(resolve), {once: true});
          Function(action)();
        })""",
        {"action": action, "event": event},
    )
    after = await page.evaluate("({...counts})")
    delta = after["renders"] - before["renders"]
    assert delta == expected_renders, (
        f"{action}: expected {expected_renders} renders, got {delta}"
    )
    assert after["closes"] - before["closes"] == (expected_closes or expected_renders)
    assert await page.evaluate("errors") == []
    return after


async def run_hash_routes(page):
    """Cover first opening, two browser events, repeated URLs and direct renders."""
    assert await page.evaluate("counts.renders") == 1
    await transition(page, "goTo('#/first')", 1)
    assert await page.evaluate("events") == ["popstate", "hashchange"]
    assert await page.evaluate("counts.boards") == 1
    before = await page.evaluate("({...counts})")
    await page.evaluate("goTo('#/first'); new Promise(requestAnimationFrame)")
    assert await page.evaluate("({...counts})") == before
    await page.evaluate("state.lang = 'ru'; render()")
    assert await page.evaluate("counts.renders") == before["renders"] + 1
    await page.evaluate("goHome()")
    await transition(page, "goTo('#/first')", 1)
    await transition(page, "goTo('#/second')", 1)
    await transition(page, "history.back()", 1)
    assert await page.evaluate("parseRoute().slug") == "first"
    await transition(page, "history.forward()", 1)
    assert await page.evaluate("parseRoute().slug") == "second"
    await page.evaluate("goHome()")
    adopted = await transition(
        page, "goTo('#/first/k/synthetic')", 1, expected_closes=2
    )
    assert adopted["adopted"] == 1
    assert await page.evaluate("location.hash") == "#/first"
    await transition(page, "goTo('#/first/deliver')", 1)
    assert await page.evaluate("parseRoute().view") == "deliver"
    print(
        "PASS hash: first opening, paired events, same URL, direct render, A/home/A, back/forward, adoption, deliver"
    )


async def run_real_paths(page):
    """Cover real guest routes and history entries created by goHome."""
    assert await page.evaluate("parseRoute()") == {"view": "board", "slug": "first"}
    assert await page.evaluate("counts.boards") == 1
    await page.evaluate("goHome()")
    await transition(page, "history.back()", 1, "popstate")
    assert await page.evaluate("parseRoute().slug") == "first"
    await transition(page, "history.forward()", 1, "popstate")
    assert await page.evaluate("parseRoute().view") == "landing"
    await transition(page, "goTo('#/second')", 1)
    await page.evaluate("goHome()")
    await transition(page, "goTo('#/second')", 1)
    print(
        "PASS real path: first opening, home, back/forward, subsequent hash transitions"
    )


async def run(source, executable=CHROME):
    """Run extracted production functions with synthetic in-memory boundaries.

    Use the selected Chrome executable, defaulting to the macOS installation.
    """
    router = extract_router(source)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=executable, headless=True
        )
        try:
            for path, scenario in (
                ("/", run_hash_routes),
                ("/c/first", run_real_paths),
            ):
                context = await browser.new_context()
                page = await context.new_page()
                page.set_default_timeout(5000)
                await page.route(
                    "**/*",
                    lambda route, request, path=path: (
                        route.fulfill(
                            status=200,
                            content_type="text/html",
                            body='<main id="app"></main>',
                        )
                        if route.request.url == ORIGIN + path
                        else route.abort()
                    ),
                )
                await page.goto(ORIGIN + path)
                await page.add_script_tag(content=BOUNDARIES + router)
                await scenario(page)
                await context.close()
        finally:
            await browser.close()
    print(
        json.dumps(
            {
                "scope": "router component; counted renderer/WS boundaries, not full app",
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "passed": 2,
                "failed": 0,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=Path(__file__).parents[1] / "frontend/app.js"
    )
    parser.add_argument(
        "--executable",
        default=CHROME,
        help="Chrome executable path (default: macOS Chrome)",
    )
    args = parser.parse_args()
    asyncio.run(
        asyncio.wait_for(run(args.source.read_text(), args.executable), timeout=40)
    )
