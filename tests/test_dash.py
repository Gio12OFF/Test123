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
    assert manifest.segment_urls == [
        "https://media.example.test/movie/720/v1/chunk-00007.m4s",
        "https://media.example.test/movie/1080/v2/chunk-00007.m4s",
    ]
    assert [(item.kind, item.language) for item in manifest.renditions] == [
        ("audio", "en"),
        ("text", "uk"),
    ]


def test_rejects_non_mpd_xml():
    with pytest.raises(ManifestError, match="root element"):
        parse_dash("<playlist />", "https://example.test/manifest.mpd")


def test_parses_representation_segment_list():
    manifest = parse_dash(
        """<MPD><Period><AdaptationSet contentType="video">
        <Representation id="video" bandwidth="1000">
          <BaseURL>video/</BaseURL>
          <SegmentList><SegmentURL media="first.m4s" /></SegmentList>
        </Representation>
        </AdaptationSet></Period></MPD>""",
        "https://cdn.example.test/manifest.mpd",
    )

    assert manifest.segment_urls == ["https://cdn.example.test/video/first.m4s"]
