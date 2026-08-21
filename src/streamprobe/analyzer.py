from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import httpx

from streamprobe.exceptions import ManifestError
from streamprobe.expiry import detect_url_expiry
from streamprobe.models import SegmentProbe, StreamKind, StreamReport, Variant
from streamprobe.parsers import parse_dash, parse_hls
from streamprobe.scoring import health_score
from streamprobe.security import validate_public_http_url

HLS_CONTENT_TYPES = {
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "audio/mpegurl",
}
DASH_CONTENT_TYPES = {"application/dash+xml"}
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_SEGMENT_SAMPLE_BYTES = 64 * 1024
MAX_REDIRECTS = 5


class StreamAnalyzer:
    def __init__(
        self,
        *,
        timeout: float = 10.0,
        segment_samples: int = 3,
        concurrency: int = 4,
        allow_private: bool = False,
        user_agent: str = "StreamProbe/0.3 (+https://github.com/Gio12OFF/Test123)",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.timeout = timeout
        self.segment_samples = max(0, segment_samples)
        self.concurrency = max(1, concurrency)
        self.allow_private = allow_private
        self.user_agent = user_agent
        self._client = client

    async def analyze(self, url: str) -> StreamReport:
        validate_public_http_url(url, allow_private=self.allow_private)
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=False,
            trust_env=False,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/vnd.apple.mpegurl,application/dash+xml,*/*",
            },
        )
        try:
            started = time.perf_counter()
            try:
                body, final_url, status_code, content_type = await self._fetch_limited(
                    client, url, limit=MAX_MANIFEST_BYTES
                )
                if not 200 <= status_code < 300:
                    raise ManifestError(f"Manifest request failed: HTTP {status_code}")
            except httpx.HTTPError as exc:
                raise ManifestError(f"Manifest request failed: {exc}") from exc
            manifest_latency = (time.perf_counter() - started) * 1000
            manifest = self._parse(body.decode("utf-8", errors="replace"), final_url, content_type)
            expiry = detect_url_expiry(final_url)
            segment_urls = manifest.segment_urls[: self.segment_samples]
            discovery_warnings: list[str] = []
            if (
                manifest.kind is StreamKind.HLS
                and not segment_urls
                and manifest.variants
                and self.segment_samples
            ):
                segment_urls, discovery_warnings = await self._discover_hls_segments(
                    client, manifest.variants, self.segment_samples
                )
            segments = await self._probe_segments(client, segment_urls)
            warnings = [
                *discovery_warnings,
                *self._warnings(
                    manifest.kind, manifest.variants, segments, expiry.seconds_remaining
                ),
            ]
            return StreamReport(
                manifest=manifest,
                manifest_latency_ms=round(manifest_latency, 2),
                manifest_status_code=status_code,
                segments=segments,
                url_expiry=expiry,
                health_score=health_score(segments, expiry, warnings),
                warnings=warnings,
                checked_at=datetime.now(timezone.utc),
            )
        finally:
            if owns_client:
                await client.aclose()

    async def _fetch_limited(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        limit: int,
        headers: dict[str, str] | None = None,
    ) -> tuple[bytes, str, int, str]:
        current_url = url
        for redirect_count in range(MAX_REDIRECTS + 1):
            validate_public_http_url(current_url, allow_private=self.allow_private)
            # StreamProbe intentionally requests a user-selected stream. Every initial and
            # redirected URL is constrained to HTTP(S), resolved, and rejected when any
            # address is non-global. Response sizes, redirects, and timeouts are also bounded.
            # codeql[py/full-ssrf]
            async with client.stream(
                "GET",
                current_url,
                headers=headers,
            ) as response:
                if response.is_redirect and response.headers.get("location"):
                    if redirect_count == MAX_REDIRECTS:
                        raise ManifestError(f"Too many redirects (>{MAX_REDIRECTS})")
                    current_url = urljoin(str(response.url), response.headers["location"])
                    continue
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > limit:
                        raise ManifestError(f"Response exceeds safety limit of {limit} bytes")
                return (
                    bytes(body),
                    str(response.url),
                    response.status_code,
                    response.headers.get("content-type", ""),
                )
        raise ManifestError("Redirect handling failed")

    async def _discover_hls_segments(
        self,
        client: httpx.AsyncClient,
        variants: list[Variant],
        limit: int,
    ) -> tuple[list[str], list[str]]:
        selected = self._representative_variants(variants, min(limit, len(variants)))
        semaphore = asyncio.Semaphore(self.concurrency)

        async def media_segments(variant: Variant) -> list[str]:
            current_url = variant.uri
            try:
                async with semaphore:
                    for _depth in range(3):
                        body, final_url, status_code, _ = await self._fetch_limited(
                            client, current_url, limit=MAX_MANIFEST_BYTES
                        )
                        if not 200 <= status_code < 300:
                            return []
                        playlist = parse_hls(body.decode("utf-8", errors="replace"), final_url)
                        if playlist.segment_urls:
                            return playlist.segment_urls
                        if not playlist.variants:
                            return []
                        current_url = max(
                            playlist.variants, key=lambda item: item.bandwidth or 0
                        ).uri
            except Exception:
                return []
            return []

        playlists = list(await asyncio.gather(*(media_segments(item) for item in selected)))
        segments: list[str] = []
        index = 0
        while len(segments) < limit and any(index < len(items) for items in playlists):
            for items in playlists:
                if index < len(items) and items[index] not in segments:
                    segments.append(items[index])
                    if len(segments) == limit:
                        break
            index += 1

        failures = sum(not items for items in playlists)
        warnings = (
            [f"Could not inspect {failures} of {len(playlists)} HLS variant playlists"]
            if failures
            else []
        )
        return segments, warnings

    @staticmethod
    def _representative_variants(variants: list[Variant], limit: int) -> list[Variant]:
        ordered = sorted(variants, key=lambda item: item.bandwidth or 0)
        if limit <= 0:
            return []
        if limit == 1:
            return ordered[-1:]
        if len(ordered) <= limit:
            return ordered
        indexes = [round(index * (len(ordered) - 1) / (limit - 1)) for index in range(limit)]
        return [ordered[index] for index in indexes]

    @staticmethod
    def _parse(text: str, url: str, content_type: str):
        media_type = content_type.split(";", 1)[0].strip().lower()
        stripped = text.lstrip("\ufeff\n\r \t")
        if (
            media_type in HLS_CONTENT_TYPES
            or stripped.startswith("#EXTM3U")
            or url.lower().split("?", 1)[0].endswith(".m3u8")
        ):
            return parse_hls(text, url)
        if (
            media_type in DASH_CONTENT_TYPES
            or "<MPD" in stripped[:500]
            or url.lower().split("?", 1)[0].endswith(".mpd")
        ):
            return parse_dash(text, url)
        raise ManifestError("Unsupported manifest: expected HLS (#EXTM3U) or DASH (MPD)")

    async def _probe_segments(
        self, client: httpx.AsyncClient, urls: list[str]
    ) -> list[SegmentProbe]:
        semaphore = asyncio.Semaphore(self.concurrency)

        async def probe(url: str) -> SegmentProbe:
            async with semaphore:
                try:
                    validate_public_http_url(url, allow_private=self.allow_private)
                    started = time.perf_counter()
                    body, final_url, status_code, _ = await self._fetch_limited(
                        client,
                        url,
                        limit=MAX_SEGMENT_SAMPLE_BYTES,
                        headers={"Range": "bytes=0-65535"},
                    )
                    latency = (time.perf_counter() - started) * 1000
                    return SegmentProbe(
                        uri=final_url,
                        status_code=status_code,
                        latency_ms=round(latency, 2),
                        size_bytes=len(body),
                        available=200 <= status_code < 300,
                    )
                except Exception as exc:  # a failed sample belongs in the report
                    return SegmentProbe(uri=url, error=str(exc), available=False)

        return list(await asyncio.gather(*(probe(url) for url in urls)))

    @staticmethod
    def _warnings(kind, variants, segments, seconds_remaining) -> list[str]:
        warnings: list[str] = []
        if not variants and kind is StreamKind.DASH:
            warnings.append("No video representations found")
        failed = [segment for segment in segments if not segment.available]
        if failed:
            warnings.append(f"{len(failed)} of {len(segments)} sampled segments unavailable")
        slow = [segment for segment in segments if (segment.latency_ms or 0) > 500]
        if slow:
            warnings.append(f"{len(slow)} sampled segments slower than 500 ms")
        if seconds_remaining is not None and seconds_remaining <= 0:
            warnings.append("Signed URL appears to be expired")
        elif seconds_remaining is not None and seconds_remaining < 1800:
            warnings.append(
                f"Signed URL expires in about {max(0, seconds_remaining // 60)} minutes"
            )
        return warnings


async def analyze(url: str, **options) -> StreamReport:
    """Analyze a stream URL with a short-lived analyzer."""
    return await StreamAnalyzer(**options).analyze(url)
