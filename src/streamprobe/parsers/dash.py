from __future__ import annotations

import re
from urllib.parse import urljoin
from xml.etree import ElementTree

from streamprobe.exceptions import ManifestError
from streamprobe.models import ManifestInfo, Rendition, StreamKind, Variant
from streamprobe.parsers.common import parse_float, parse_int

ISO_DURATION_RE = re.compile(
    r"^P(?:(?P<days>[\d.]+)D)?(?:T(?:(?P<hours>[\d.]+)H)?"
    r"(?:(?P<minutes>[\d.]+)M)?(?:(?P<seconds>[\d.]+)S)?)?$"
)
DASH_TEMPLATE_RE = re.compile(
    r"\$(?P<name>RepresentationID|Bandwidth|Number)(?:%0(?P<width>\d+)d)?\$"
)


def _duration(value: str | None) -> float | None:
    if not value or not (match := ISO_DURATION_RE.match(value)):
        return None
    parts = {key: float(raw or 0) for key, raw in match.groupdict().items()}
    return parts["days"] * 86400 + parts["hours"] * 3600 + parts["minutes"] * 60 + parts["seconds"]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(element: ElementTree.Element, name: str) -> str | None:
    for child in element:
        if _local_name(child.tag) == name and child.text:
            return child.text.strip()
    return None


def _child(element: ElementTree.Element, name: str) -> ElementTree.Element | None:
    return next((item for item in element if _local_name(item.tag) == name), None)


def _expand_template(template: str, representation: ElementTree.Element, number: int) -> str:
    values: dict[str, str | int] = {
        "RepresentationID": representation.attrib.get("id", ""),
        "Bandwidth": parse_int(representation.attrib.get("bandwidth")) or 0,
        "Number": number,
    }
    escaped = template.replace("$$", "\x00")

    def replacement(match: re.Match[str]) -> str:
        value = values[match.group("name")]
        width = parse_int(match.group("width"))
        if width and isinstance(value, int):
            return f"{value:0{width}d}"
        return str(value)

    return DASH_TEMPLATE_RE.sub(replacement, escaped).replace("\x00", "$")


def parse_dash(text: str, url: str) -> ManifestInfo:
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        raise ManifestError(f"Invalid DASH manifest: {exc}") from exc
    if _local_name(root.tag) != "MPD":
        raise ManifestError("Invalid DASH manifest: root element must be MPD")

    base = urljoin(url, _child_text(root, "BaseURL") or "")
    variants: list[Variant] = []
    renditions: list[Rendition] = []
    segment_urls: list[str] = []
    for adaptation in root.iter():
        if _local_name(adaptation.tag) != "AdaptationSet":
            continue
        content_type = (
            adaptation.attrib.get("contentType")
            or adaptation.attrib.get("mimeType", "").split("/", 1)[0]
        )
        language = adaptation.attrib.get("lang")
        if content_type in {"audio", "text", "subtitle"}:
            renditions.append(
                Rendition(kind=content_type, language=language, name=adaptation.attrib.get("label"))
            )
        adaptation_base = urljoin(base, _child_text(adaptation, "BaseURL") or "")
        adaptation_template = _child(adaptation, "SegmentTemplate")
        adaptation_segment_list = _child(adaptation, "SegmentList")
        for representation in adaptation:
            if _local_name(representation.tag) != "Representation" or content_type not in {
                "video",
                "",
            }:
                continue
            representation_base = urljoin(
                adaptation_base, _child_text(representation, "BaseURL") or ""
            )
            codecs = representation.attrib.get("codecs") or adaptation.attrib.get("codecs", "")
            variants.append(
                Variant(
                    uri=representation_base,
                    bandwidth=parse_int(representation.attrib.get("bandwidth")),
                    width=parse_int(representation.attrib.get("width")),
                    height=parse_int(representation.attrib.get("height")),
                    codecs=[codecs] if codecs else [],
                    frame_rate=parse_float(representation.attrib.get("frameRate")),
                )
            )
            template = _child(representation, "SegmentTemplate")
            if template is None:
                template = adaptation_template
            if template is not None and template.attrib.get("media"):
                number = parse_int(template.attrib.get("startNumber")) or 1
                media = _expand_template(template.attrib["media"], representation, number)
                if "$" not in media:
                    segment_urls.append(urljoin(representation_base, media))
                continue
            segment_list = _child(representation, "SegmentList")
            if segment_list is None:
                segment_list = adaptation_segment_list
            if segment_list is not None:
                segment = _child(segment_list, "SegmentURL")
                if segment is not None and segment.attrib.get("media"):
                    segment_urls.append(urljoin(representation_base, segment.attrib["media"]))

    return ManifestInfo(
        kind=StreamKind.DASH,
        url=url,
        is_live=root.attrib.get("type", "static") == "dynamic",
        duration_seconds=_duration(root.attrib.get("mediaPresentationDuration")),
        variants=variants,
        renditions=renditions,
        segment_urls=list(dict.fromkeys(segment_urls)),
    )
