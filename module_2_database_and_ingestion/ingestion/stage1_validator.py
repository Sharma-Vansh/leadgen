"""
Stage 1: Ingestion Validation Gate
Enforces structural integrity, URL validity, domain safety, and schema conformance.
"""
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse
import re
import logging
from pydantic import ValidationError
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("Stage1Validator")

# Blocked spam or phishing domain keywords
BLOCKED_DOMAINS = {
    "free-crypto-giveaway.xyz",
    "scam-jobs-portal.top",
    "phishing-careers.click"
}


class ValidationResult:
    def __init__(self):
        self.valid_records: List[Dict[str, Any]] = []
        self.rejected_records: List[Dict[str, Any]] = []

    @property
    def total_count(self) -> int:
        return len(self.valid_records) + len(self.rejected_records)

    @property
    def valid_count(self) -> int:
        return len(self.valid_records)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected_records)


class Stage1Validator:
    """Validates raw job payloads or StandardJobListing instances before normalization."""

    @classmethod
    def validate_single(cls, raw_data: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates a single job record.
        Returns (validated_dict, None) on success or (None, rejection_reason) on failure.
        """
        if not raw_data or not isinstance(raw_data, (dict, StandardJobListing)):
            return None, "Empty payload or invalid record type"

        # Convert to dictionary if already a Pydantic model
        if isinstance(raw_data, StandardJobListing):
            data = raw_data.model_dump()
        else:
            data = dict(raw_data)

        # 1. Validate Title
        title = data.get("title")
        if not title or not isinstance(title, str) or len(title.strip()) < 2:
            return None, "Title is missing, non-string, or less than 2 characters"

        # 2. Validate Company (Default for Govt notices if missing)
        company = data.get("company")
        source_id = str(data.get("source_id", ""))
        archetype = str(data.get("archetype", ""))
        
        if not company or not isinstance(company, str) or not company.strip():
            if "SRC-02" in source_id or archetype.upper() == "C":
                company = "Central / State Government Recruitment"
                data["company"] = company
            else:
                return None, "Company name is missing or empty"

        # 3. Validate Apply URL
        apply_url = data.get("apply_url")
        if not apply_url or not isinstance(apply_url, str):
            return None, "Application URL is missing or non-string"

        apply_url = apply_url.strip()
        parsed_url = urlparse(apply_url)
        if not parsed_url.scheme or parsed_url.scheme not in ("http", "https"):
            return None, f"Application URL '{apply_url}' has invalid protocol (must be http/https)"
        if not parsed_url.netloc or "." not in parsed_url.netloc:
            return None, f"Application URL '{apply_url}' does not have a valid domain network location"

        # 4. Domain Safety Check
        domain_lower = parsed_url.netloc.lower()
        if any(blocked in domain_lower for blocked in BLOCKED_DOMAINS):
            return None, f"Application URL domain '{parsed_url.netloc}' is on the security blocklist"

        # 5. Clean basic whitespace
        data["title"] = " ".join(title.split()).strip()
        data["company"] = " ".join(company.split()).strip()
        data["apply_url"] = apply_url

        return data, None

    @classmethod
    def validate_batch(cls, records: List[Any]) -> ValidationResult:
        """
        Validates a batch of job listings.
        Returns a ValidationResult object with valid and rejected records.
        """
        result = ValidationResult()

        for idx, item in enumerate(records):
            valid_dict, reason = cls.validate_single(item)
            if valid_dict:
                result.valid_records.append(valid_dict)
            else:
                logger.warning(f"[Stage1Validator] Dropped record index {idx}: {reason}")
                result.rejected_records.append({
                    "raw_payload": item if isinstance(item, dict) else str(item),
                    "reason": reason,
                    "index": idx
                })

        logger.info(
            f"[Stage1Validator] Processed {result.total_count} records: "
            f"{result.valid_count} valid, {result.rejected_count} rejected."
        )
        return result
