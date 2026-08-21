"""StreamProbe public library API."""

from streamprobe.analyzer import StreamAnalyzer, analyze
from streamprobe.models import StreamReport

__all__ = ["StreamAnalyzer", "StreamReport", "analyze"]
__version__ = "0.1.0"
