from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from streamprobe.models import URLExpiry

EXPIRY_KEYS = ("expires", "exp", "expiry", "e", "x-amz-expires")
AMZ_DATE_FORMAT = "%Y%m%dT%H%M%SZ"


def _as_epoch(value: str) -> datetime | None:
    if not re.fullmatch(r"\d{9,13}", value):
        return None
    epoch = int(value)
    if epoch > 10_000_000_000:
        epoch //= 1000
    try:
        return datetime.fromtimestamp(epoch, tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        return None


def _jwt_exp(value: str) -> datetime | None:
    parts = value.split(".")
    if len(parts) != 3:
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        return _as_epoch(str(payload.get("exp", "")))
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def detect_url_expiry(url: str, now: datetime | None = None) -> URLExpiry:
    now = now or datetime.now(timezone.utc)
    query = {
        key.lower(): values[0] for key, values in parse_qs(urlparse(url).query).items() if values
    }
    expires_at: datetime | None = None
    source: str | None = None

    amz_date = query.get("x-amz-date")
    amz_ttl = query.get("x-amz-expires")
    if amz_date and amz_ttl:
        try:
            signed_at = datetime.strptime(amz_date, AMZ_DATE_FORMAT).replace(tzinfo=timezone.utc)
            expires_at = datetime.fromtimestamp(
                signed_at.timestamp() + int(amz_ttl), tz=timezone.utc
            )
            source = "X-Amz-Expires"
        except (ValueError, OverflowError):
            pass

    if expires_at is None:
        for key in EXPIRY_KEYS:
            if value := query.get(key):
                if parsed := _as_epoch(value):
                    expires_at, source = parsed, key
                    break

    if expires_at is None:
        for key, value in query.items():
            if parsed := _jwt_exp(value):
                expires_at, source = parsed, f"{key}.jwt.exp"
                break

    if expires_at is None:
        return URLExpiry()
    return URLExpiry(
        detected=True,
        expires_at=expires_at,
        seconds_remaining=int((expires_at - now).total_seconds()),
        source_parameter=source,
    )
