# Architecture

StreamProbe keeps protocol parsing separate from network I/O. This makes parsers deterministic, easy to fuzz, and safe to test with synthetic manifests.

## Data flow

1. `security.py` accepts only absolute HTTP(S) URLs and rejects non-global resolved addresses unless local access is explicitly enabled.
2. `analyzer.py` fetches the manifest with a bounded timeout and follows redirects.
3. Content, content type, and final URL select the HLS or DASH parser.
4. A parser returns a protocol-neutral `ManifestInfo` model.
5. The analyzer samples a bounded number of HLS media segments concurrently with byte-range requests.
6. `expiry.py` recognizes common epoch, AWS, and JWT expiry signals without attempting to validate or bypass signatures.
7. `scoring.py` deducts points for unavailable/slow samples, near expiry, and warnings.
8. Typed results feed the CLI, REST API, dashboard, and metrics endpoint.

## Module boundaries

| Module | Responsibility |
| --- | --- |
| `models.py` | Stable protocol-neutral result schema |
| `parsers/hls.py` | Pure HLS tag and URI parsing |
| `parsers/dash.py` | Pure MPD representation parsing |
| `analyzer.py` | Fetching, concurrency, orchestration |
| `security.py` | Target network policy |
| `expiry.py` | Signed URL lifetime hints |
| `scoring.py` | Explainable health calculation |
| `api.py` / `cli.py` | User-facing adapters |

## Extension rules

- Parser changes should use fixture-based unit tests and must not perform network requests.
- Network checks should be opt-in or bounded by `segment_samples`, timeout, and concurrency.
- New output fields belong in the Pydantic models before they appear in a UI.
- Scores must remain explainable; every deduction should correspond to observable report data.
- Provider-specific behavior should live behind a generic capability, never a provider scraper.

## Current limits

- DASH representations are parsed, but SegmentTemplate/SegmentTimeline sampling is planned.
- HLS encryption metadata is not reported yet; StreamProbe will report declarations only and will not retrieve keys.
- DNS rebinding protection is best-effort. Production operators should also apply outbound firewall and proxy rules.
- The in-process Prometheus counters are intentionally minimal and reset on restart.
