from __future__ import annotations

from streamprobe.models import StreamReport


def human_report(report: StreamReport) -> str:
    manifest = report.manifest
    live = "live" if manifest.is_live else "VOD" if manifest.is_live is False else "master"
    lines = [
        f"✓ Manifest: {manifest.kind.value} ({live})",
        f"✓ Response: HTTP {report.manifest_status_code} in {report.manifest_latency_ms:.0f} ms",
        f"✓ Variants: {len(manifest.variants)}",
    ]
    for variant in sorted(manifest.variants, key=lambda item: item.bandwidth or 0):
        bitrate = (
            f"{(variant.bandwidth or 0) / 1_000_000:.2f} Mbps"
            if variant.bandwidth
            else "unknown bitrate"
        )
        codecs = ", ".join(variant.codecs) or "unknown codec"
        lines.append(f"  {variant.resolution:<12} {bitrate:<13} {codecs}")
    if report.segments:
        average = sum(item.latency_ms or 0 for item in report.segments) / len(report.segments)
        lines.append(
            f"✓ Segments: {report.available_segments}/{len(report.segments)} available; "
            f"average {average:.0f} ms"
        )
    if report.url_expiry.detected:
        minutes = (report.url_expiry.seconds_remaining or 0) // 60
        lines.append(f"⚠ Signed URL expiry: {minutes} minutes")
    lines.extend(f"⚠ {warning}" for warning in report.warnings)
    lines.append("")
    lines.append(f"Stream health: {report.health_score}/100")
    return "\n".join(lines)
