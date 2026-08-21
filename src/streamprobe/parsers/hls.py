from __future__ import annotations

from streamprobe.exceptions import ManifestError
from streamprobe.models import ManifestInfo, Rendition, StreamKind, Variant
from streamprobe.parsers.common import (
    absolute_url,
    parse_attribute_list,
    parse_float,
    parse_int,
)


def parse_hls(text: str, url: str) -> ManifestInfo:
    lines = [line.strip() for line in text.lstrip("\ufeff").splitlines() if line.strip()]
    if not lines or lines[0] != "#EXTM3U":
        raise ManifestError("Invalid HLS manifest: missing #EXTM3U header")

    variants: list[Variant] = []
    renditions: list[Rendition] = []
    segments: list[str] = []
    duration = 0.0
    pending_variant: dict[str, str] | None = None
    has_endlist = False

    for line in lines[1:]:
        if line.startswith("#EXT-X-STREAM-INF:"):
            pending_variant = parse_attribute_list(line.partition(":")[2])
            continue
        if line.startswith("#EXT-X-MEDIA:"):
            attrs = parse_attribute_list(line.partition(":")[2])
            renditions.append(
                Rendition(
                    kind=attrs.get("TYPE", "UNKNOWN").lower(),
                    name=attrs.get("NAME"),
                    language=attrs.get("LANGUAGE"),
                    uri=absolute_url(url, attrs["URI"]) if attrs.get("URI") else None,
                )
            )
            continue
        if line.startswith("#EXTINF:"):
            duration += parse_float(line.partition(":")[2].split(",", 1)[0]) or 0
            continue
        if line == "#EXT-X-ENDLIST":
            has_endlist = True
            continue
        if line.startswith("#"):
            continue

        resource_url = absolute_url(url, line)
        if pending_variant is not None:
            resolution = pending_variant.get("RESOLUTION", "").split("x", 1)
            width = parse_int(resolution[0]) if len(resolution) == 2 else None
            height = parse_int(resolution[1]) if len(resolution) == 2 else None
            variants.append(
                Variant(
                    uri=resource_url,
                    bandwidth=parse_int(
                        pending_variant.get("AVERAGE-BANDWIDTH") or pending_variant.get("BANDWIDTH")
                    ),
                    width=width,
                    height=height,
                    codecs=[
                        codec.strip()
                        for codec in pending_variant.get("CODECS", "").split(",")
                        if codec.strip()
                    ],
                    frame_rate=parse_float(pending_variant.get("FRAME-RATE")),
                    audio_group=pending_variant.get("AUDIO"),
                )
            )
            pending_variant = None
        else:
            segments.append(resource_url)

    is_media_playlist = bool(segments) or "#EXT-X-TARGETDURATION:" in text
    return ManifestInfo(
        kind=StreamKind.HLS,
        url=url,
        is_live=not has_endlist if is_media_playlist else None,
        duration_seconds=round(duration, 3) if duration else None,
        variants=variants,
        renditions=renditions,
        segment_urls=segments,
    )
