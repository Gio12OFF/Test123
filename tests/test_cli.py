import json
from datetime import datetime, timezone

from typer.testing import CliRunner

from streamprobe.cli import app
from streamprobe.models import ManifestInfo, StreamKind, StreamReport


def _report() -> StreamReport:
    return StreamReport(
        manifest=ManifestInfo(kind=StreamKind.HLS, url="https://example.test/master.m3u8"),
        manifest_latency_ms=12.5,
        manifest_status_code=200,
        health_score=100,
        checked_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def test_jsonl_emits_exactly_one_compact_json_object(monkeypatch):
    async def fake_analyze(self, url):
        return _report()

    monkeypatch.setattr("streamprobe.cli.StreamAnalyzer.analyze", fake_analyze)
    result = CliRunner().invoke(app, ["inspect", "https://example.test/master.m3u8", "--jsonl"])

    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 1
    assert "\n" not in result.stdout.rstrip("\n")
    assert json.loads(result.stdout)["health_score"] == 100


def test_json_and_jsonl_are_mutually_exclusive():
    result = CliRunner().invoke(
        app, ["inspect", "https://example.test/master.m3u8", "--json", "--jsonl"]
    )

    assert result.exit_code == 2
    assert "cannot be used together" in result.output
