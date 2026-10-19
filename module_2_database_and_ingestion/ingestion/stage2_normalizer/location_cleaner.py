"""
Stage 2 Normalizer: Location Cleaner
Normalizes city aliases, regional variations, and remote flags.
"""
from typing import Optional, Tuple
import re

CITY_ALIASES = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "blr": "Bangalore",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "navimumbai": "Navi Mumbai",
    "navi mumbai": "Navi Mumbai",
    "delhi": "Delhi NCR",
    "newdelhi": "New Delhi",
    "new delhi": "New Delhi",
    "ncr": "Delhi NCR",
    "delhincr": "Delhi NCR",
    "gurugram": "Gurgaon",
    "gurgaon": "Gurgaon",
    "noida": "Noida",
    "greaternoida": "Greater Noida",
    "greater noida": "Greater Noida",
    "hyderabad": "Hyderabad",
    "secunderabad": "Hyderabad",
    "pune": "Pune",
    "chennai": "Chennai",
    "madras": "Chennai",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "ahmedabad": "Ahmedabad",
    "chandigarh": "Chandigarh",
    "jaipur": "Jaipur",
    "kochi": "Kochi",
    "coimbatore": "Coimbatore",
    "indore": "Indore",
    "bhopal": "Bhopal",
    "lucknow": "Lucknow",
    "thiruvananthapuram": "Thiruvananthapuram",
    "trivandrum": "Thiruvananthapuram"
}

REMOTE_PATTERNS = [
    r"\bremote\b",
    r"\bwfh\b",
    r"\bwork from home\b",
    r"\btelecommute\b",
    r"\banywhere\b",
    r"\bvirtual\b"
]


class LocationCleaner:
    """Standardizes geographic representations and detects remote modality."""

    @classmethod
    def clean(cls, raw_location: Optional[str]) -> Tuple[str, bool, str, Optional[str]]:
        """
        Cleans location string.
        Returns: (canonical_location_string, is_remote_bool, country_string, canonical_city)
        """
        if not raw_location or not isinstance(raw_location, str):
            return "Remote", True, "India", None

        loc = " ".join(raw_location.split()).strip()
        loc_lower = loc.lower()

        # Check for remote indicators
        is_remote = any(re.search(pat, loc_lower) for pat in REMOTE_PATTERNS)

        # Check for canonical city
        matched_city = None
        for alias, canonical in CITY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", loc_lower):
                matched_city = canonical
                break

        # Check for country
        country = "India"
        if any(c in loc_lower for c in ["usa", "united states", "us", "uk", "united kingdom", "germany", "canada", "singapore", "australia"]):
            if "india" not in loc_lower:
                if any(u in loc_lower for u in ["usa", "united states", "us"]):
                    country = "United States"
                elif any(u in loc_lower for u in ["uk", "united kingdom", "london"]):
                    country = "United Kingdom"
                elif "germany" in loc_lower:
                    country = "Germany"
                elif "canada" in loc_lower:
                    country = "Canada"
                elif "singapore" in loc_lower:
                    country = "Singapore"
                elif "australia" in loc_lower:
                    country = "Australia"

        # Canonical string
        if matched_city:
            if is_remote:
                canonical_location = f"{matched_city} / Remote"
            else:
                canonical_location = f"{matched_city}, {country}" if country != "India" else f"{matched_city}, India"
        elif is_remote:
            canonical_location = "Remote / Pan India" if country == "India" else f"Remote, {country}"
        else:
            canonical_location = loc

        return canonical_location, is_remote, country, matched_city
