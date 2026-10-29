"""Page inspection and evidence capture utilities.
Reference: Section 7.3 of AGENTS.md.
"""

from __future__ import annotations
import hashlib
import os
import re
import unicodedata
from datetime import datetime, timezone
from io import BytesIO
from typing import Any
from PIL import Image
from civiclens.models import Evidence, EvidenceKind


def normalize_text(text: str) -> str:
    """Normalizes text: Unicode NFC, whitespace collapsed."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", normalized).strip()


def compute_dom_hash(dom_content: str) -> str:
    """Computes SHA-256 hash of serialized DOM."""
    return hashlib.sha256(dom_content.encode("utf-8")).hexdigest()


def crop_element_bbox(
    screenshot_bytes: bytes,
    bbox: list[float],
    output_path: str,
    padding: int = 24
) -> str:
    """Crops an element from a screenshot with 24px padding and saves as WebP."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with Image.open(BytesIO(screenshot_bytes)) as img:
        img_w, img_h = img.size
        x, y, w, h = bbox
        
        # Apply padding and clamp to image dimensions
        left = max(0, int(x - padding))
        top = max(0, int(y - padding))
        right = min(img_w, int(x + w + padding))
        bottom = min(img_h, int(y + h + padding))
        
        # Ensure non-zero crop area
        if right <= left:
            right = min(img_w, left + 10)
        if bottom <= top:
            bottom = min(img_h, top + 10)

        cropped = img.crop((left, top, right, bottom))
        cropped.save(output_path, "WEBP", quality=80)
        return output_path


def build_evidence(
    scan_id: str,
    page_id: str,
    page_url: str,
    idx: int,
    kind: EvidenceKind,
    text: str,
    device: str = "desktop",
    context: str = "",
    selector: str | None = None,
    role: str | None = None,
    accessible_name: str | None = None,
    href: str | None = None,
    bbox: list[float] | None = None,
    crop_path: str | None = None,
    axe_rule_id: str | None = None,
    wcag_tags: list[str] | None = None,
    dom_hash: str = ""
) -> Evidence:
    """Helper to create a validated Evidence object."""
    ev_id = f"ev_{page_id}_{idx}"
    clean_text = normalize_text(text)
    clean_context = normalize_text(context)[:300] if context else ""
    return Evidence(
        id=ev_id,
        scan_id=scan_id,
        page_id=page_id,
        page_url=page_url,
        device="mobile" if device == "mobile" else "desktop",
        kind=kind,
        selector=selector,
        role=role,
        accessible_name=accessible_name,
        text=clean_text,
        context=clean_context,
        href=href,
        bbox=bbox,
        crop_path=crop_path,
        axe_rule_id=axe_rule_id,
        wcag_tags=wcag_tags or [],
        dom_snapshot_hash=dom_hash,
        captured_at=datetime.now(timezone.utc)
    )
