# Changelog

All notable changes will be documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project intends to follow semantic versioning after its first stable release.

## [Unreleased]

## [0.3.0] - 2026-08-21

### Added

- Nullable HLS rendition flags for `DEFAULT`, `AUTOSELECT`, and `FORCED`.
- Provider-neutral AV1 and VP9 family/profile labels in API, terminal, and dashboard output.
- Compact `--jsonl` CLI output for pipelines and repeated checks.

## [0.2.0] - 2026-08-21

### Added

- Automatic traversal from HLS master playlists into representative media playlists.
- Segment sampling across the HLS bitrate ladder instead of stopping at the master manifest.
- DASH `SegmentTemplate` expansion for representation ID, bandwidth, and numbered media URLs.
- DASH `SegmentList` support for directly declared media segments.

### Changed

- Updated the default user agent and package version to 0.2.0.

## [0.1.0] - 2026-08-21

### Added

- HLS master/media playlist parsing with variants and renditions.
- DASH representation, rendition, live/VOD, and duration parsing.
- bounded segment availability and latency sampling.
- common signed URL expiry detection.
- explainable stream health score.
- CLI, typed Python API, REST API, web dashboard, and Prometheus metrics.
- Docker image configuration and GitHub Actions automation.
- contributor, security, governance, roadmap, and Claude OSS documentation.
