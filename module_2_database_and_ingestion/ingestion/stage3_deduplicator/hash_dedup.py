"""
Stage 3 Deduplicator: Level 1 Exact Hash Engine
Computes deterministic SHA-256 fingerprints to eliminate duplicate job postings in O(1) time.
"""
import hashlib
import re
from typing import Optional, Dict, Any


class HashDeduplicator:
    """Computes and validates deterministic SHA-256 hashes for fast exact deduplication."""

    @classmethod
    def compute_hash(
        cls,
        company: str,
        title: str,
        city: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Generates a canonical SHA-256 hash from normalized company, title, and geographic scope.
        """
        # Canonical string stripping (lowercase alphanumeric only)
        c_clean = re.sub(r"[^a-z0-9]", "", (company or "").lower())
        t_clean = re.sub(r"[^a-z0-9]", "", (title or "").lower())
        loc_str = city or location or "remote"
        l_clean = re.sub(r"[^a-z0-9]", "", loc_str.lower())

        raw_fingerprint = f"{c_clean}_{t_clean}_{l_clean}"
        return hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

    @classmethod
    def generate_for_listing(cls, listing_dict: Dict[str, Any]) -> str:
        """Helper to generate hash directly from normalized listing dictionary."""
        return cls.compute_hash(
            company=listing_dict.get("company", ""),
            title=listing_dict.get("title", ""),
            city=listing_dict.get("city"),
            location=listing_dict.get("location")
        )
