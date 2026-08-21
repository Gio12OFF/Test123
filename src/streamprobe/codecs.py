from __future__ import annotations


def friendly_codec_label(codec: str) -> str | None:
    """Return a provider-neutral AV1/VP9 label without rewriting the raw value."""
    parts = codec.strip().lower().split(".")
    family = parts[0]

    if family in {"av01", "av1"}:
        profiles = {"0": "Main", "1": "High", "2": "Professional"}
        profile = profiles.get(parts[1]) if len(parts) > 1 else None
        return f"AV1 {profile} profile" if profile else "AV1"

    if family in {"vp09", "vp9"}:
        profile = parts[1].lstrip("0") or "0" if len(parts) > 1 else None
        return f"VP9 Profile {profile}" if profile is not None and profile.isdigit() else "VP9"

    return None


def display_codec(codec: str) -> str:
    label = friendly_codec_label(codec)
    return f"{codec} ({label})" if label else codec
