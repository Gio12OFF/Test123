from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from streamprobe.exceptions import UnsafeURLError


def validate_public_http_url(url: str, *, allow_private: bool = False) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeURLError("Only absolute HTTP(S) URLs are supported")
    if allow_private:
        return
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port)}
    except socket.gaierror as exc:
        raise UnsafeURLError(f"Could not resolve host: {parsed.hostname}") from exc
    for raw in addresses:
        address = ipaddress.ip_address(raw)
        if not address.is_global:
            raise UnsafeURLError(f"Private or reserved address is blocked: {address}")
