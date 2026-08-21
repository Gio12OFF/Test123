from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse

from streamprobe import __version__
from streamprobe.analyzer import StreamAnalyzer
from streamprobe.exceptions import StreamProbeError
from streamprobe.models import StreamReport
from streamprobe.monitoring import metrics

STATIC_DIR = Path(__file__).with_name("static")
app = FastAPI(
    title="StreamProbe API",
    version=__version__,
    description="Analyze HLS and DASH manifests, variants, segment latency, expiry, and health.",
)


@app.get("/", include_in_schema=False)
async def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz", tags=["operations"])
async def healthz() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/metrics", response_class=PlainTextResponse, tags=["operations"])
async def prometheus_metrics() -> str:
    return metrics.render()


@app.get("/api/v1/analyze", response_model=StreamReport, tags=["analysis"])
async def analyze_stream(
    url: str = Query(min_length=8, description="Public HTTP(S) HLS or DASH manifest URL"),
    samples: int = Query(default=3, ge=0, le=20),
) -> StreamReport:
    try:
        report = await StreamAnalyzer(segment_samples=samples).analyze(url)
    except StreamProbeError as exc:
        metrics.record_failure()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    metrics.record_success(report.health_score)
    return report
