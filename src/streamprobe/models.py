from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, computed_field

from streamprobe.codecs import friendly_codec_label


class StreamKind(str, Enum):
    HLS = "HLS"
    DASH = "DASH"


class Variant(BaseModel):
    uri: str
    bandwidth: int | None = None
    width: int | None = None
    height: int | None = None
    codecs: list[str] = Field(default_factory=list)
    frame_rate: float | None = None
    audio_group: str | None = None

    @computed_field
    @property
    def codec_labels(self) -> list[str | None]:
        """Human-friendly labels while preserving the raw codec declarations."""
        return [friendly_codec_label(codec) for codec in self.codecs]

    @property
    def resolution(self) -> str:
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "unknown"


class Rendition(BaseModel):
    kind: str
    name: str | None = None
    language: str | None = None
    uri: str | None = None
    default: bool | None = None
    autoselect: bool | None = None
    forced: bool | None = None


class SegmentProbe(BaseModel):
    uri: str
    status_code: int | None = None
    latency_ms: float | None = None
    size_bytes: int | None = None
    available: bool = False
    error: str | None = None


class URLExpiry(BaseModel):
    detected: bool = False
    expires_at: datetime | None = None
    seconds_remaining: int | None = None
    source_parameter: str | None = None


class ManifestInfo(BaseModel):
    kind: StreamKind
    url: str
    is_live: bool | None = None
    duration_seconds: float | None = None
    variants: list[Variant] = Field(default_factory=list)
    renditions: list[Rendition] = Field(default_factory=list)
    segment_urls: list[str] = Field(default_factory=list, exclude=True)


class StreamReport(BaseModel):
    manifest: ManifestInfo
    manifest_latency_ms: float
    manifest_status_code: int
    segments: list[SegmentProbe] = Field(default_factory=list)
    url_expiry: URLExpiry = Field(default_factory=URLExpiry)
    health_score: int = Field(ge=0, le=100)
    warnings: list[str] = Field(default_factory=list)
    checked_at: datetime

    @property
    def available_segments(self) -> int:
        return sum(segment.available for segment in self.segments)
