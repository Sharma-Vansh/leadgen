"""
Stage 2 Normalizer: Employment Type Classifier
Classifies raw job titles and employment type descriptions into canonical enums.
"""
from typing import Optional, Tuple
import re

CANONICAL_TYPES = {
    "full_time",
    "part_time",
    "internship",
    "contract",
    "gig"
}


class TypeClassifier:
    """Classifies employment types from title, raw type string, and job descriptions."""

    @classmethod
    def classify(
        cls,
        raw_type: Optional[str],
        title: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Classifies employment into (canonical_type, confidence).
        confidence is 'high', 'medium', or 'default'.
        """
        text = f"{raw_type or ''} {title or ''}".lower()

        # 1. Internship / Trainee Detection
        if any(term in text for term in ["intern", "internship", "trainee", "apprentice", "fellowship", "fellow"]):
            return "internship", "high"

        # 2. Gig / Delivery / Driver / Helper (e.g. Porter, Dunzo, Zomato rider)
        if any(term in text for term in ["gig", "delivery partner", "rider", "driver", "biker", "field executive"]):
            return "gig", "high"

        # 3. Contract / Freelance
        if any(term in text for term in ["contract", "contractual", "freelance", "temp", "temporary", "consultant"]):
            return "contract", "high"

        # 4. Part-Time
        if any(term in text for term in ["part-time", "part time", "parttime"]):
            return "part_time", "high"

        # 5. Explicit Full-Time
        if any(term in text for term in ["full-time", "full time", "fulltime", "permanent", "regular"]):
            return "full_time", "high"

        # Direct enum match on raw_type
        if raw_type and raw_type.lower() in CANONICAL_TYPES:
            return raw_type.lower(), "high"

        # Default fallback
        return "full_time", "default"
