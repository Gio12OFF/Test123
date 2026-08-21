# StreamProbe

[![CI](https://github.com/Gio12OFF/Test123/actions/workflows/ci.yml/badge.svg)](https://github.com/Gio12OFF/Test123/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-6e56cf)](LICENSE)
[![Built with Claude Code](https://img.shields.io/badge/built%20with-Claude%20Code-D97757?logo=anthropic&logoColor=white)](https://www.anthropic.com/claude-code)
[![Fast PR reviews](https://img.shields.io/badge/PR%20reviews-within%2048h-16a34a)](CONTRIBUTING.md)

**Open-source HLS/DASH stream analyzer and monitoring toolkit. Inspect manifests, codecs, resolutions, segment latency, URL expiration, and stream health from your terminal or browser.**

StreamProbe gives video, CDN, and platform engineers one consistent way to answer a deceptively hard question: *is this adaptive stream healthy right now?* It is protocol-focused, provider-neutral, and designed to be useful as a CLI, Python library, REST service, or monitoring component.

> [!TIP]
> **Contributors are welcome.** Focused pull requests usually receive an initial review within 48 hours and are merged as soon as their scope, tests, and CI are ready.

> [!IMPORTANT]
> Only probe streams you own or are authorized to test. StreamProbe samples a small byte range from a few segments; it does not download, decrypt, bypass access controls, or redistribute video.

## What it checks

- HLS master and media playlists (`.m3u8`)
- MPEG-DASH manifests (`.mpd`)
- automatic HLS master-to-media traversal across representative bitrate variants
- basic DASH `SegmentTemplate` and `SegmentList` media URL resolution
- variants, resolution, bandwidth, frame rate, and codec declarations
- audio and subtitle renditions, including default/autoselect/forced flags
- provider-neutral AV1 and VP9 family/profile labels (raw codec values remain available)
- sampled segment availability and response latency
- common signed URL expiry formats, including AWS query signatures and JWT expiry
- live/VOD detection and declared duration
- explainable stream health score from 0 to 100
- JSON output, REST API, web dashboard, and Prometheus metrics
- public-target validation to reduce SSRF risk in server deployments

## Quick start

StreamProbe is currently an early source release. Install it from this repository:

```bash
python -m pip install "git+https://github.com/Gio12OFF/Test123.git"
streamprobe inspect "https://cdn.example.com/video/master.m3u8"
```

Example output:

```text
✓ Manifest: HLS (master)
✓ Response: HTTP 200 in 82 ms
✓ Variants: 4
  640x360      0.80 Mbps     avc1.4d401e
  1280x720     2.50 Mbps     avc1.64001f
  1920x1080    5.20 Mbps     avc1.640028
  3840x2160    14.10 Mbps    hvc1.1.6.L153.B0
✓ Segments: 3/3 available; average 96 ms
⚠ Signed URL expires in about 17 minutes

Stream health: 91/100
```

Machine-readable output is available with `--json`:

```bash
streamprobe inspect URL --json --samples 5 --timeout 8
```

Use compact JSON Lines when piping a result into an automation process:

```bash
streamprobe inspect URL --jsonl | jq -c 'select(.health_score < 80)'
```

API responses expose raw `codecs` alongside `codec_labels`; HLS renditions include
nullable `default`, `autoselect`, and `forced` fields.

Private and localhost targets are blocked by default. For local development only, pass `--allow-private`.

## Python library

```python
import asyncio
from streamprobe import analyze

report = asyncio.run(analyze("https://cdn.example.com/master.m3u8"))
print(report.health_score)
for variant in report.manifest.variants:
    print(variant.resolution, variant.bandwidth, variant.codecs)
```

All results are typed [Pydantic](https://docs.pydantic.dev/) models and serialize cleanly with `report.model_dump(mode="json")`.

## REST API and dashboard

```bash
python -m pip install -e ".[api]"
streamprobe serve --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` for the dashboard, `/docs` for OpenAPI, or query the API directly:

```bash
curl --get http://localhost:8000/api/v1/analyze \
  --data-urlencode "url=https://cdn.example.com/master.m3u8"
```

Operational endpoints:

| Endpoint | Purpose |
| --- | --- |
| `/healthz` | container/readiness health |
| `/metrics` | Prometheus text metrics |
| `/docs` | interactive OpenAPI documentation |

## Docker

```bash
docker run --rm -p 8000:8000 ghcr.io/gio12off/streamprobe:latest
# or build locally
docker compose up --build
```

The container runs as an unprivileged user and includes a health check.

## Architecture

```text
URL
 ├─ network safety validation
 ├─ manifest fetch and protocol detection
 │   ├─ HLS parser
 │   └─ DASH parser
 ├─ variant / rendition extraction
 ├─ bounded concurrent segment probes
 ├─ signed URL expiry detector
 └─ explainable health score
      ├─ CLI / JSON
      ├─ Python API
      ├─ REST API + dashboard
      └─ Prometheus metrics
```

Read [the architecture guide](docs/ARCHITECTURE.md) for module boundaries and extension points.

## Project status

StreamProbe is **alpha software**. Its parser and analyzer core work, including representative HLS variant traversal and basic DASH segment URL resolution, but protocol edge cases vary enormously across packagers and CDNs. That makes real-world fixtures and focused improvements especially valuable.

The [roadmap](docs/ROADMAP.md) contains 30 scoped contribution ideas, including AV1/VP9 normalization, deeper DASH segment probing, LL-HLS checks, Grafana dashboards, Windows packaging, and exporters. Issues marked `good first issue` should be independently testable and small enough for a first contribution.

## Contributing

Contributions from video engineers, Python developers, documentation writers, and first-time OSS contributors are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), read the [Code of Conduct](CODE_OF_CONDUCT.md), and open a discussion before large architectural changes.

When contributing a manifest fixture, remove tokens, hostnames, user identifiers, and media URLs. Prefer a minimal synthetic fixture that reproduces the parser behavior.

## Responsible development and attribution

This project was developed with assistance from [Claude Code](https://www.anthropic.com/claude-code). The maintainer remains responsible for design decisions, review, security, and releases. StreamProbe is an independent open-source project and is not affiliated with or endorsed by Anthropic.

See [docs/CLAUDE_OSS.md](docs/CLAUDE_OSS.md) for the project story and a transparent draft description for the Claude for Open Source program.

## License

Licensed under the [Apache License 2.0](LICENSE). Copyright 2026 StreamProbe contributors.
