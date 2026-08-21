from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass
class Metrics:
    analyses_total: int = 0
    failures_total: int = 0
    last_health_score: int = 0

    def __post_init__(self) -> None:
        self._lock = Lock()

    def record_success(self, score: int) -> None:
        with self._lock:
            self.analyses_total += 1
            self.last_health_score = score

    def record_failure(self) -> None:
        with self._lock:
            self.analyses_total += 1
            self.failures_total += 1

    def render(self) -> str:
        with self._lock:
            return "\n".join(
                [
                    "# HELP streamprobe_analyses_total Total stream analyses.",
                    "# TYPE streamprobe_analyses_total counter",
                    f"streamprobe_analyses_total {self.analyses_total}",
                    "# HELP streamprobe_failures_total Failed stream analyses.",
                    "# TYPE streamprobe_failures_total counter",
                    f"streamprobe_failures_total {self.failures_total}",
                    "# HELP streamprobe_last_health_score Last calculated health score.",
                    "# TYPE streamprobe_last_health_score gauge",
                    f"streamprobe_last_health_score {self.last_health_score}",
                    "",
                ]
            )


metrics = Metrics()
