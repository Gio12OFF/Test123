from streamprobe.models import SegmentProbe, URLExpiry
from streamprobe.scoring import health_score


def test_healthy_samples_keep_high_score():
    samples = [
        SegmentProbe(uri=f"https://cdn.test/{index}.ts", available=True, latency_ms=80)
        for index in range(3)
    ]
    assert health_score(samples, URLExpiry(), []) == 100


def test_failures_latency_and_warnings_reduce_score():
    samples = [
        SegmentProbe(uri="https://cdn.test/1.ts", available=True, latency_ms=1300),
        SegmentProbe(uri="https://cdn.test/2.ts", available=False),
    ]
    assert health_score(samples, URLExpiry(), ["problem"]) < 60
