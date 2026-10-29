"""Unit tests for SSRF protection and URL validation.
Reference: Section 14 of AGENTS.md.
"""

from civiclens.security import is_ip_private_or_restricted, validate_url, _match_pattern


def test_domain_pattern_matching():
    assert _match_pattern("*.gov.in", "scholarships.gov.in")
    assert _match_pattern("*.gov.in", "sub.portal.gov.in")
    assert _match_pattern("*.gov.in", "gov.in")
    assert _match_pattern("*.nic.in", "scholarships.nic.in")
    assert not _match_pattern("*.gov.in", "evil-gov.in.com")
    assert not _match_pattern("*.gov.in", "gov.in.attacker.org")


def test_ip_restriction_checks():
    # Loopback
    assert is_ip_private_or_restricted("127.0.0.1")
    assert is_ip_private_or_restricted("::1")
    # Private
    assert is_ip_private_or_restricted("10.0.0.1")
    assert is_ip_private_or_restricted("192.168.1.1")
    assert is_ip_private_or_restricted("172.16.0.5")
    # Link local
    assert is_ip_private_or_restricted("169.254.1.1")
    # AWS/GCP metadata
    assert is_ip_private_or_restricted("169.254.169.254")
    # Public IP
    assert not is_ip_private_or_restricted("8.8.8.8")
    assert not is_ip_private_or_restricted("1.1.1.1")


def test_validate_url_rejections():
    # Reject non-https
    ok, msg = validate_url("http://scholarships.gov.in/")
    assert not ok
    assert "scheme must be 'https'" in msg

    # Reject non-allowlisted domains
    ok, msg = validate_url("https://google.com/")
    assert not ok
    assert "not in the allowed domain list" in msg

    # Reject empty
    ok, msg = validate_url("")
    assert not ok
