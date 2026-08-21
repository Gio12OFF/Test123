# Roadmap and contribution map

This is a living list, not a promise of release dates. Each item is intentionally scoped so it can become a self-contained GitHub issue. Maintainers should add acceptance criteria and fixtures before applying `good first issue`.

## 0.2 — Protocol depth

1. Normalize H.264 codec profile and level names.
2. Add AV1 codec normalization and friendly labels.
3. Add VP9 codec normalization and friendly labels.
4. Report HEVC/H.265 profiles and tiers.
5. Detect HLS audio-only and iframe-only variants.
6. Report HLS subtitle characteristics and forced/default flags.
7. Parse HLS encryption declarations without fetching keys.
8. Validate HLS target duration against observed segment durations.
9. Detect discontinuities and sequence gaps.
10. Add LL-HLS part and preload-hint checks.

## 0.3 — DASH and transport

11. ✅ Resolve basic DASH `SegmentTemplate` URLs.
12. Support DASH `SegmentTimeline` sampling.
13. Read DASH initialization segments with bounded ranges.
14. Report DASH content protection declarations without bypass logic.
15. Detect UTC timing drift for dynamic MPDs.
16. Add redirect-chain diagnostics.
17. Report DNS, connect, TLS, TTFB, and download timings separately.
18. Add IPv4/IPv6 comparison mode.
19. Add configurable request headers with secret redaction.
20. Add retry policy and per-attempt reporting.

## 0.4 — Monitoring and ecosystem

21. Add a persistent watch command with interval and threshold flags.
22. Add Prometheus labels for target and protocol with cardinality safeguards.
23. Publish an example Grafana dashboard.
24. Add JSON Lines output for monitoring pipelines.
25. Add OpenTelemetry traces.
26. Add a GitHub Action for scheduled stream checks.
27. Publish signed multi-architecture container images.
28. Add standalone Windows, macOS, and Linux CLI builds.
29. Add a plugin interface for custom health rules.
30. Build a privacy-safe corpus of synthetic real-world manifest edge cases.

## Release principles

- Correctness and safety before feature count.
- Backwards-compatible result schemas within a minor release.
- No provider scraping or DRM bypass features.
- Every network feature needs explicit limits, redaction, and tests.
