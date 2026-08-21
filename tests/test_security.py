import socket

import pytest

from streamprobe.exceptions import UnsafeURLError
from streamprobe.security import validate_public_http_url


def test_blocks_non_http_protocol():
    with pytest.raises(UnsafeURLError, match="HTTP"):
        validate_public_http_url("file:///etc/passwd")


def test_blocks_private_resolved_address(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))],
    )
    with pytest.raises(UnsafeURLError, match="blocked"):
        validate_public_http_url("http://internal.example/")


def test_can_explicitly_allow_private_target():
    validate_public_http_url("http://127.0.0.1:8000/stream.m3u8", allow_private=True)
