"""Unit tests for exact quote matching (Gate G3).
Reference: Section 8.4 of AGENTS.md.
"""

from civiclens.scan.capture import build_evidence
from civiclens.ai.verify import check_quote_match, normalize_quote


def test_quote_normalization():
    # Whitespace collapse & case-folding
    assert normalize_quote("  Click   HERE  \n ") == "click here"
    # Unicode NFC normalization
    hindi_str = "यहाँ  क्लिक  करें"
    assert normalize_quote(hindi_str) == "यहाँ क्लिक करें"


def test_quote_match_success():
    ev = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=1, kind="link", text="Click here to download", context="Rules and conditions"
    )
    assert check_quote_match("Click here", ev)
    assert check_quote_match("click HERE", ev)
    assert check_quote_match("download", ev)
    # Context match supported when allow_context=True
    assert check_quote_match("Rules and conditions", ev, allow_context=True)
    assert not check_quote_match("Rules and conditions", ev, allow_context=False)


def test_quote_match_failure():
    ev = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=1, kind="link", text="Click here to download", context="Rules and conditions"
    )
    # Non-existent phrase
    assert not check_quote_match("Submit application immediately", ev)
    # Empty quote
    assert not check_quote_match("", ev)
