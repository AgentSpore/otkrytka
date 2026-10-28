# Asset cache evidence

Issue [#5](https://github.com/AgentSpore/otkrytka/issues/5), PR [#6](https://github.com/AgentSpore/otkrytka/pull/6).
Generated captures are excluded from the source tip. The original eight files
remain in Git history at `8261625e1106982ec869fbe549da4241097f9782`.
The Application regression workflow extracts only those files, checks their
pinned SHA256 values (including manifest.json), and uploads them as
`issue-5-historical-db26f367-<run_id>-<run_attempt>` for 90 days.
The historical manifest lists seven payload files with byte sizes and hashes;
it does not hash itself. The workflow independently pins all eight hashes.

Open the PR's Application regression check, follow its workflow run, and find
Artifacts. A successful upload provides the actual artifact ID and download URL.
No artifact ID or URL has been verified yet. Download requires GitHub sign-in
and repository read access; access is not anonymous or permanent. Repository or
organization retention limits may shorten availability. The release maintainer must download the
real artifact, verify its hashes, and add the verified run/artifact link to PR #6.
An export/upload failure fails the job. Export follows the application gate,
so a failed gate does not produce a new artifact.

These are historical synthetic browser results for application commit
`db26f367ec6ea252fcc50d54853407a76ce11145`, not a new browser run on the
cleanup head. They exclude production/TLS/CDN acceptance. See the artifact's
README for recorded results, capture limitations and original reproduction steps.
Do not upload raw browser output: it can contain synthetic private routes and
unrelated runtime configuration.

## Reproduce

The application and fixture regression sources remain in `tests/`:

```sh
uv run --python 3.11 --locked --extra dev pytest
```

For the separate browser check, build baseline `15c90932b5d185b02891c780b7db987e96470584`
and candidate images and use their immutable image IDs. A separate older image
with different raw JavaScript is needed to demonstrate replacement of stale bytes.
Docker, socat, Chrome and matching Playwright recording dependencies are required.
Use a fresh output directory outside Git; override `--browser` for your platform.

```sh
uv run --no-project --python 3.14 --with playwright==1.64.1 python -m playwright install --no-remove ffmpeg
uv run --no-project --python 3.14 --with playwright==1.64.1 python tests/e2e/asset_cache.py \
  --old-image "$ASSET_OLD_IMAGE" --new-image "$ASSET_NEW_IMAGE" \
  --output /tmp/otkrytka-asset-evidence
```

Browser success alone does not prove fixture cleanup. Retain cleanup and signal
regressions. Production transition still requires the existing public-domain
bare `/app.js` checks; historical export does not satisfy that gate.
