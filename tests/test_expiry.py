import base64
import json
from datetime import datetime, timezone

from streamprobe.expiry import detect_url_expiry

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_detects_unix_expiry_parameter():
    result = detect_url_expiry("https://cdn.test/a.m3u8?expires=1767226500", NOW)

    assert result.detected
    assert result.seconds_remaining == 900
    assert result.source_parameter == "expires"


def test_detects_aws_relative_expiry():
    result = detect_url_expiry(
        "https://cdn.test/a.m3u8?X-Amz-Date=20260101T000000Z&X-Amz-Expires=1200",
        NOW,
    )

    assert result.detected
    assert result.seconds_remaining == 1200
    assert result.source_parameter == "X-Amz-Expires"


def test_detects_expiry_inside_jwt_query_value():
    payload = (
        base64.urlsafe_b64encode(json.dumps({"exp": 1767226200}).encode()).decode().rstrip("=")
    )
    token = f"header.{payload}.signature"
    result = detect_url_expiry(f"https://cdn.test/a.m3u8?token={token}", NOW)

    assert result.detected
    assert result.seconds_remaining == 600


def test_returns_empty_result_without_expiry_hint():
    assert not detect_url_expiry("https://cdn.test/a.m3u8?quality=high", NOW).detected
