from __future__ import annotations

from streamprobe.models import SegmentProbe, URLExpiry


def health_score(segments: list[SegmentProbe], expiry: URLExpiry, warnings: list[str]) -> int:
    score = 100.0
    if segments:
        availability = sum(segment.available for segment in segments) / len(segments)
        score -= (1 - availability) * 55
        latencies = [segment.latency_ms for segment in segments if segment.latency_ms is not None]
        if latencies:
            average = sum(latencies) / len(latencies)
            score -= min(20, max(0, average - 150) / 50)
            if max(latencies) > 1000:
                score -= 5
    else:
        score -= 5
    if expiry.detected and expiry.seconds_remaining is not None:
        if expiry.seconds_remaining <= 0:
            score -= 30
        elif expiry.seconds_remaining < 300:
            score -= 15
        elif expiry.seconds_remaining < 1800:
            score -= 5
    score -= min(10, len(warnings) * 2)
    return max(0, min(100, round(score)))
