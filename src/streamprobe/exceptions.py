class StreamProbeError(Exception):
    """Base exception for expected StreamProbe failures."""


class ManifestError(StreamProbeError):
    """The manifest could not be fetched or parsed."""


class UnsafeURLError(StreamProbeError):
    """A URL points to a target blocked by the network safety policy."""
