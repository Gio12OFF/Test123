# Contributing to StreamProbe

Thank you for helping make adaptive-stream diagnostics more useful and approachable. Contributions can be code, synthetic fixtures, tests, documentation, design, issue triage, or reproducible bug reports.

## Before you start

- Search existing issues and discussions.
- Small fixes can go directly to a pull request.
- Open an issue or discussion before a new dependency, public API change, scoring change, or large feature.
- Never submit live access tokens, customer hostnames, private manifests, media, encryption keys, or personal data.
- Do not contribute scraping, DRM circumvention, access-control bypass, or redistribution functionality.

## Development setup

```bash
git clone https://github.com/Gio12OFF/Test123.git
cd Test123
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -e ".[api,dev]"
pytest
ruff check .
ruff format --check .
```

Python 3.10 is the minimum supported version. CI also checks newer supported versions.

## A good pull request

1. Does one coherent thing and explains the user-visible reason.
2. Adds or updates tests for behavior changes.
3. Uses a minimal synthetic fixture for protocol edge cases.
4. Updates the README, architecture guide, or changelog when appropriate.
5. Preserves bounded network behavior and avoids leaking full signed URLs in new logs.
6. Passes tests, formatting, and lint checks.

Pull requests from first-time contributors are welcome. A maintainer may suggest splitting a change to keep review focused; that is a collaboration tool, not a rejection of the idea.

## Review response time

Focused pull requests usually receive an initial maintainer review within 48 hours. Small documentation, fixture, and well-tested bug-fix PRs can often be merged immediately after CI passes. Larger or security-sensitive changes may need additional review, but maintainers will keep their status clear instead of leaving contributors guessing.

## Fixture guidelines

- Prefer `.example`, `.test`, or `example.com` hostnames.
- Replace tokens and signatures with inert placeholders.
- Keep only the tags needed to reproduce the behavior.
- Do not include playable media or keys.
- Mention the packager family only if it is relevant and safe to disclose.

## Commit and review process

Clear imperative commit subjects are preferred, for example `Add LL-HLS part parsing`. Maintainers squash or rebase as appropriate and may edit the final commit message. At least one maintainer review is required; security-sensitive network changes may require two.

By contributing, you agree that your contribution is licensed under the Apache License 2.0 and that you have the right to submit it.

## Finding work

Look for `good first issue`, `help wanted`, or a scoped item in [docs/ROADMAP.md](docs/ROADMAP.md). Comment before starting so maintainers can confirm scope and avoid duplicated work.
