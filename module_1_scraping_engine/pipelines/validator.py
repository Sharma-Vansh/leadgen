"""
Validation Gate:
Ensures all scraped records conform to the StandardJobListing schema.
Filters out incomplete, broken, or junk listings before sending them downstream.
"""
from typing import List, Tuple, Any, Dict, Optional
import logging
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("PipelineValidator")


class JobValidator:
    @staticmethod
    def validate_listing(raw_data: Dict[str, Any]) -> Tuple[bool, Optional[StandardJobListing], Optional[str]]:
        """
        Validates a single job dict against the StandardJobListing schema.
        Returns: (is_valid, listing_object_or_none, error_message_or_none)
        """
        try:
            # Check mandatory fields existence before Pydantic parsing
            if not raw_data.get("title") or not str(raw_data.get("title")).strip():
                return False, None, "Missing or empty title"
            if not raw_data.get("company") or not str(raw_data.get("company")).strip():
                return False, None, "Missing or empty company"
            if not raw_data.get("apply_url") or not str(raw_data.get("apply_url")).strip().startswith("http"):
                return False, None, "Missing or invalid apply_url"

            listing = StandardJobListing(**raw_data)
            return True, listing, None
        except Exception as e:
            return False, None, str(e)

    @classmethod
    def validate_batch(cls, raw_items: List[Dict[str, Any]]) -> Tuple[List[StandardJobListing], int]:
        """
        Validates an entire batch of raw job dicts.
        Returns: (valid_listings_list, rejected_count)
        """
        valid_listings: List[StandardJobListing] = []
        rejected_count = 0

        for item in raw_items:
            is_valid, listing, err = cls.validate_listing(item)
            if is_valid and listing:
                valid_listings.append(listing)
            else:
                rejected_count += 1
                logger.debug(f"Rejected listing due to validation error: {err}")

        return valid_listings, rejected_count
