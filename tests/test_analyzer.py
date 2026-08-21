from pathlib import Path

import httpx
import pytest

from streamprobe.analyzer import StreamAnalyzer
from streamprobe.exceptions import UnsafeURLError

MEDIA = (Path(__file__).parent / "fixtures" / "media.m3u8").read_text()
MASTER = (Path(__file__).parent / "fixtures" / "master.m3u8").read_text()


@pytest.mark.asyncio
async def test_analyzer_fetches_manifest_and_bounded_segment_samples():
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        if request.url.path.endswith("index.m3u8"):
            return httpx.Response(
                200,
                text=MEDIA,
                headers={"content-type": "application/vnd.apple.mpegurl"},
                request=request,
            )
        return httpx.Response(206, content=b"segment", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await StreamAnalyzer(
            client=client,
            allow_private=True,
            segment_samples=2,
        ).analyze("https://cdn.example.test/index.m3u8")

    assert report.manifest_status_code == 200
    assert len(report.segments) == 2
    assert report.available_segments == 2
    assert len(requested) == 3
    assert report.health_score >= 90


@pytest.mark.asyncio
async def test_analyzer_validates_every_redirect_target(monkeypatch):
    checked: list[str] = []

    def validate(url: str, *, allow_private: bool = False) -> None:
        checked.append(url)
        if "127.0.0.1" in url:
            raise UnsafeURLError("private redirect blocked")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://127.0.0.1/secret"})

    monkeypatch.setattr("streamprobe.analyzer.validate_public_http_url", validate)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(UnsafeURLError, match="private redirect"):
            await StreamAnalyzer(client=client).analyze("https://public.example.test/index.m3u8")

    assert checked == [
        "https://public.example.test/index.m3u8",
        "https://public.example.test/index.m3u8",
        "http://127.0.0.1/secret",
    ]


@pytest.mark.asyncio
async def test_analyzer_discovers_segments_behind_hls_master_variants():
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        if request.url.path.endswith("master.m3u8"):
            return httpx.Response(200, text=MASTER, request=request)
        if request.url.path.endswith(("360p.m3u8", "720p.m3u8")):
            return httpx.Response(200, text=MEDIA, request=request)
        return httpx.Response(206, content=b"segment", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        report = await StreamAnalyzer(
            client=client,
            allow_private=True,
            segment_samples=2,
        ).analyze("https://cdn.example.test/master.m3u8")

    assert len(report.manifest.variants) == 2
    assert report.available_segments == 2
    assert len(report.segments) == 2
    assert any("video/360p.m3u8" in url for url in requested)
    assert any("video/720p.m3u8" in url for url in requested)
    assert not report.warnings
