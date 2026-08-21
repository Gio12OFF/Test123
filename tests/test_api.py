from fastapi.testclient import TestClient

from streamprobe.api import app


def test_dashboard_and_operational_endpoints():
    client = TestClient(app)

    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "Know your stream" in dashboard.text

    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "streamprobe_analyses_total" in metrics.text
