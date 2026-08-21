from pathlib import Path

import pytest

from streamprobe.exceptions import ManifestError
from streamprobe.parsers.dash import parse_dash

FIXTURES = Path(__file__).parent / "fixtures"


def test_parses_dash_representations_renditions_and_duration():
    manifest = parse_dash(
        (FIXTURES / "manifest.mpd").read_text(),
        "https://origin.example.test/path/manifest.mpd",
    )

    assert manifest.kind.value == "DASH"
    assert manifest.is_live is False
    assert manifest.duration_seconds == 90
    assert [variant.resolution for variant in manifest.variants] == ["1280x720", "1920x1080"]
    assert manifest.variants[0].uri == "https://media.example.test/movie/720/"
    assert [(item.kind, item.language) for item in manifest.renditions] == [
        ("audio", "en"),
        ("text", "uk"),
    ]


def test_rejects_non_mpd_xml():
    with pytest.raises(ManifestError, match="root element"):
        parse_dash("<playlist />", "https://example.test/manifest.mpd")
