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

    return ManifestInfo(
        kind=StreamKind.DASH,
        url=url,
        is_live=root.attrib.get("type", "static") == "dynamic",
        duration_seconds=_duration(root.attrib.get("mediaPresentationDuration")),
        variants=variants,
        renditions=renditions,
    )
