from streamprobe.codecs import display_codec, friendly_codec_label
from streamprobe.models import Variant


def test_labels_common_av1_and_vp9_declarations_without_changing_raw_values():
    variant = Variant(
        uri="https://example.test/video.m3u8",
        codecs=["av01.0.08M.08", "vp09.02.10.10.01.09.16.09.01"],
    )

    assert variant.codecs == ["av01.0.08M.08", "vp09.02.10.10.01.09.16.09.01"]
    assert variant.codec_labels == ["AV1 Main profile", "VP9 Profile 2"]


def test_labels_partial_codec_declarations():
    assert friendly_codec_label("av01") == "AV1"
    assert friendly_codec_label("vp9") == "VP9"
    assert friendly_codec_label("vp09.00") == "VP9 Profile 0"


def test_unknown_codec_remains_unmodified():
    assert friendly_codec_label("avc1.640028") is None
    assert display_codec("avc1.640028") == "avc1.640028"
    assert Variant(uri="https://example.test/video.m3u8", codecs=["avc1.640028"]).codec_labels == [
        None
    ]
