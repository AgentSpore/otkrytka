# Frontend asset rollback evidence

Status: verified locally on 2026-10-25; candidate `db26f367`, macOS ARM64, Docker and Chrome.

These artifacts exercise [issue #5](https://github.com/AgentSpore/otkrytka/issues/5)
with local application images, a shared synthetic data volume, a real nginx cache
and Chrome. Browser caching remained enabled; requests were not intercepted.
They do not establish production, TLS or Cloudflare cache acceptance.

## Results

| Case | Observed result | Evidence |
| --- | --- | --- |
| Exact baseline/candidate | A new document's CSS was held, the application rolled back, then the browser received matching CSS and JS through the network. SHA, MIME and SRI checks passed. | [Exact proof](exact-proof.json) |
| Live cancellation | SIGTERM sent to the exact owned Python PID after HTTP 200. Expected interrupted exit 1; no forced kill; cleanup passed. | [Cancellation proof](cancellation-proof.json) |
| Historical older JS | While the new application was active, legacy `/app.js` remained a cache HIT with SHA `9693f06c…`; generated HTML referenced JS `0845b3eb…`. After rollback, the browser fetched both generated assets with the correct bytes. | [Historical proof](historical-proof.json) |

The coordinator also ran the final complete application/fixture suite: 154 passed,
0 skipped in 2.68 seconds. Both complete browser cases checked five HTML entry points, organizer/guest interaction,
live updates and reload. Browser errors were empty. Teardown removed all owned
resources without failures and preserved the original unrelated container set.
The exact pair has identical raw JS/CSS, so only the historical case establishes
replacement of genuinely different stale JS bytes.

The application image was built from `db26f367`; its application sources and raw
frontend bytes are unchanged by the later test/documentation commits. Proofs
retain immutable local image IDs and the browser harness SHA used by each run.
Synthetic board paths are replaced with route templates in published JSON.

## Reviewed captures

The captures below come from the historical case. Both final screenshots show
an open live connection. No private organizer link or token is displayed.

- [Guest, 390 × 844](guest-390.png)
- [Organizer, 1440 × 900](organizer-1440.png)
- [Mobile recording, WebM](guest-flow.webm): VP9, 368 × 800, 6.32 seconds.

The uncut recording covers mobile interaction and reload, including initial
paint and a temporary reconnect before the final live state. It does not record
the earlier rollback phase; the browser byte/network proofs cover that phase.
Chrome's default recording size scales the 390 × 844 viewport to 368 × 800.

## Run locally

The normal application suite includes the fixture's filesystem, signal and
subprocess regressions without requiring Docker or Playwright:

```sh
uv run --locked --extra dev pytest -q
```

For the separate real-browser scenario, build the old and new application
images first. Set `ASSET_OLD_IMAGE` and `ASSET_NEW_IMAGE` to their immutable
`sha256:` IDs. Set `DOCKER_HOST` for your local daemon when needed. The default
browser path targets Chrome on macOS; override it with `--browser` elsewhere.
The fixture also requires Docker and socat. Its containers are capped at a
combined 1024 MiB and 1.9 CPU, use unique ownership labels, and create only
synthetic data. Use a fresh output directory for each run.

```sh
uv run --no-project --python 3.14 --with playwright==1.64.1 python -m playwright install --no-remove ffmpeg
uv run --no-project --python 3.14 --with playwright==1.64.1 python tests/e2e/asset_cache.py \
  --old-image "$ASSET_OLD_IMAGE" --new-image "$ASSET_NEW_IMAGE" \
  --output /tmp/otkrytka-asset-evidence
```

The tested baseline is `15c90932`; a separate historical image with different
raw JS is necessary for the stale-cache comparison. The recording dependency
must match the pinned Playwright version. `SIGTERM` or `SIGINT` unwinds the
owned fixture; a successful browser assertion alone does not establish cleanup.

Existing browser/CDN objects still require an explicit production transition.
The separate release acceptance continues checking bare `/app.js` on both
public domains. These results do not authorize replacing that gate with a
cache-busted or origin-only request.
