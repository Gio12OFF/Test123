# Claude for Open Source project description

This page is a transparent project narrative and a draft that can be adapted for an application. It must be updated with real adoption and contribution data before submission; it intentionally makes no claims about popularity that the repository cannot prove.

## Short description

**StreamProbe is an open-source HLS/DASH diagnostics and monitoring toolkit for video and CDN engineers. It turns a manifest URL into a typed report covering variants, codecs, renditions, sampled segment availability and latency, signed URL lifetime, and an explainable health score. The same core is available through a Python API, CLI, REST service, browser dashboard, Prometheus endpoint, and container image.**

## Ecosystem value

Adaptive streaming failures often sit between applications, packagers, CDNs, signing systems, and players. Existing debugging is commonly a mixture of `curl`, browser tools, and protocol-specific utilities. StreamProbe aims to provide a small, automation-friendly first diagnostic that works across HLS and DASH and produces a stable JSON schema suitable for CI and monitoring.

The project is provider-neutral and deliberately excludes scraping, access-control bypass, DRM circumvention, and media redistribution. Its network work is bounded, its server mode blocks private targets by default, and fixtures are expected to be synthetic and token-free.

## Why the community can contribute

Streaming protocols contain many independent tags, codecs, packager quirks, and observability integrations. The roadmap breaks these into reviewable units: codec normalization, manifest edge cases, timing metrics, exporters, packaging, documentation, and test fixtures. A contributor can improve one capability without needing access to a private video platform.

Community health should be measured honestly through merged external contributions, repeat contributors, issue response time, releases, downstream usage, and security handling—not manufactured stars, downloads, or contributor accounts.

## Use of Claude Code

Claude Code assisted with implementation and documentation during the repository's development. Human maintainers remain accountable for architecture, testing, review, security decisions, attribution, and releases. This repository is not presented as sponsored, endorsed, or audited by Anthropic.

Useful future Claude Code work may include:

- turning sanitized protocol reports into minimal regression fixtures;
- proposing test matrices for parser changes;
- reviewing documentation for first-time contributor clarity;
- assisting maintainers with issue triage and release notes;
- checking that new diagnostics preserve safety limits and secret redaction.

## Application checklist

- Replace this draft with verified repository metrics and direct links.
- Link several meaningful external pull requests and describe their impact.
- Document maintainer responsiveness and release cadence.
- Include real examples of downstream or production use with permission.
- Confirm the program's current eligibility and application terms on Anthropic's official website.
- Never imply that Claude usage itself proves eligibility or project impact.

## Current eligibility reality

As checked on 21 August 2026, the [official Claude for Open Source page](https://claude.com/contact-sales/claude-for-oss) lists several independent qualification paths: maintaining packages with 500+ dependent repositories, 100+ dependent packages, or 200,000+ combined monthly registry downloads; being a core contributor to a recognized foundation or language project; having 100+ pull requests merged into repositories you do not own in the last 12 months; maintaining a repository with 20+ unique external contributors whose pull requests were merged in the last 12 months; or maintaining infrastructure with an OpenSSF criticality score of at least 0.4. Anthropic also invites maintainers of quietly important ecosystem projects to explain their impact even when they do not fit a numeric threshold.

A newly published StreamProbe repository does **not** satisfy those thresholds merely because it has a complete codebase or mentions Claude Code. The responsible path is to ship useful releases, support genuine users, make contribution tasks clear, merge valuable external work, and apply only with verifiable evidence. The program currently offers accepted applicants six months of Claude Max 20x; terms and eligibility may change, so the official page must be rechecked before applying.
