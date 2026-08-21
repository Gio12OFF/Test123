"""Minimal example of StreamProbe's typed library API."""

import asyncio

from streamprobe import analyze


async def main() -> None:
    report = await analyze("https://cdn.example.com/video/master.m3u8")
    print(f"Health: {report.health_score}/100")
    for variant in report.manifest.variants:
        print(variant.resolution, variant.bandwidth, variant.codecs)


if __name__ == "__main__":
    asyncio.run(main())
