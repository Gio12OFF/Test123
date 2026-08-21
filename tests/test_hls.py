from pathlib import Path

import pytest

from streamprobe.exceptions import ManifestError
from streamprobe.parsers.hls import parse_hls

FIXTURES = Path(__file__).parent / "fixtures"


def test_parses_master_playlist_variants_and_renditions():
    manifest = parse_hls(
        (FIXTURES / "master.m3u8").read_text(),
        "https://cdn.example.test/path/master.m3u8",
    )

    assert manifest.kind.value == "HLS"
    assert manifest.is_live is None
    assert len(manifest.variants) == 2
    assert manifest.variants[1].resolution == "1280x720"
    assert manifest.variants[1].bandwidth == 2_500_000
    assert manifest.variants[0].uri == "https://cdn.example.test/path/video/360p.m3u8"
    assert {item.kind for item in manifest.renditions} == {"audio", "subtitles"}
    audio = next(item for item in manifest.renditions if item.kind == "audio")
    subtitles = next(item for item in manifest.renditions if item.kind == "subtitles")
    assert (audio.default, audio.autoselect, audio.forced) == (True, True, None)
    assert (subtitles.default, subtitles.autoselect, subtitles.forced) == (False, True, True)

    serialized = manifest.model_dump(mode="json")
    assert serialized["renditions"][1]["forced"] is True


def test_parses_vod_media_playlist_segments_and_duration():
    manifest = parse_hls(
        (FIXTURES / "media.m3u8").read_text(),
        "https://cdn.example.test/vod/index.m3u8",
    )

    assert manifest.is_live is False
    assert manifest.duration_seconds == 16
    assert len(manifest.segment_urls) == 3
    assert manifest.segment_urls[0] == "https://cdn.example.test/vod/segments/42.ts"


def test_rejects_invalid_hls():
    with pytest.raises(ManifestError, match="#EXTM3U"):
        parse_hls("not a playlist", "https://example.test/file.m3u8")
