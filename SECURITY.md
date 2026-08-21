# Security policy

## Supported versions

Until StreamProbe reaches 1.0, security fixes are provided for the latest released minor version.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature under **Security → Advisories → Report a vulnerability**. Do not open a public issue for a vulnerability or include a working exploit, signed stream URL, credential, private hostname, or customer data in public discussions.

Include the affected version, impact, minimal reproduction, and any suggested mitigation. You should receive an acknowledgement within 5 business days and a status update within 10 business days. Timelines for a fix depend on severity and complexity.

## Security model

StreamProbe processes untrusted manifests and makes outbound requests. Its server mode blocks targets resolving to private, loopback, link-local, multicast, and reserved addresses by default, applies the same validation to every redirect, ignores proxy settings inherited from the process environment, limits redirect depth, and caps bytes read from manifests and segment samples. This is defense in depth, not a complete sandbox: DNS rebinding cannot be eliminated at the application layer alone, so production deployments should also use egress firewall rules, a dedicated restrictive proxy configured in code, timeouts, container isolation, and resource limits.

StreamProbe does not attempt to bypass authentication or DRM, retrieve encryption keys, or download complete media. New features must preserve that boundary.
