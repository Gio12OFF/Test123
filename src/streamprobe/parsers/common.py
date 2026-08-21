from __future__ import annotations

import re
from urllib.parse import urljoin

ATTRIBUTE_RE = re.compile(r'([A-Z0-9-]+)=("[^"]*"|[^,]*)')


def parse_attribute_list(value: str) -> dict[str, str]:
    return {key: raw.strip('"') for key, raw in ATTRIBUTE_RE.findall(value)}


def absolute_url(base_url: str, value: str) -> str:
    return urljoin(base_url, value.strip())


def parse_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None
