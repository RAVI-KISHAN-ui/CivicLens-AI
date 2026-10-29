"""SSRF protection and URL validation for CivicLens.
Reference: Section 14 of AGENTS.md.
"""

import ipaddress
import os
import re
import socket
from urllib.parse import urlparse

DEFAULT_ALLOWLIST = ["*.gov.in", "*.nic.in"]


def _match_pattern(pattern: str, hostname: str) -> bool:
    """Matches a wildcard domain pattern like '*.gov.in' against hostname."""
    pattern = pattern.lower().strip()
    hostname = hostname.lower().strip()

    if pattern.startswith("*."):
        suffix = pattern[1:]  # e.g. .gov.in
        return hostname.endswith(suffix) or hostname == pattern[2:]
    return hostname == pattern


def is_ip_private_or_restricted(ip_str: str) -> bool:
    """Checks whether an IP address is private, loopback, link-local, or cloud metadata."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True

    # Check for IPv4 mapped in IPv6
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    if ip.is_loopback:
        return True
    if ip.is_private:
        return True
    if ip.is_link_local:
        return True
    if ip.is_multicast:
        return True
    if ip.is_reserved:
        return True
    if ip.is_unspecified:
        return True

    # Cloud metadata check
    if str(ip) == "169.254.169.254":
        return True

    return False


def validate_url(url: str, extra_allowed_domains: list[str] | None = None) -> tuple[bool, str]:
    """Validates that a URL satisfies all SSRF rules:
    1. Scheme must be HTTPS (or HTTP only if ALLOW_LOCAL_HTTP=1 in dev/test)
    2. Host must match allowlist (*.gov.in, *.nic.in, + explicit extras)
    3. Host must resolve to a valid non-private IP
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty."

    parsed = urlparse(url)
    allow_local = os.getenv("ALLOW_LOCAL_HTTP", "0") == "1"

    if allow_local and parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1"):
        return True, "Allowed for local testing."

    if parsed.scheme != "https":
        return False, f"URL scheme must be 'https', got '{parsed.scheme}'."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL has no valid hostname."

    # Build allowlist
    env_domains = [d.strip() for d in os.getenv("ALLOWED_DOMAINS", "").split(",") if d.strip()]
    allowlist = DEFAULT_ALLOWLIST + env_domains + (extra_allowed_domains or [])

    domain_allowed = any(_match_pattern(pat, hostname) for pat in allowlist)
    if not domain_allowed:
        return False, f"Domain '{hostname}' is not in the allowed domain list (*.gov.in, *.nic.in)."

    # DNS check
    try:
        addrinfo = socket.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)
        for _, _, _, _, sockaddr in addrinfo:
            ip_str = sockaddr[0]
            if is_ip_private_or_restricted(ip_str):
                return False, f"Resolved IP '{ip_str}' is in a private, loopback, or metadata range."
    except socket.gaierror as e:
        return False, f"Failed to resolve hostname '{hostname}': {e}"

    return True, "Valid."
