"""
Data Normalization Pipeline:
- Normalizes salaries to standard annual INR
- Cleans and canonicalizes locations
- Formats dates to ISO-8601 (YYYY-MM-DD)
- Normalizes employment types
"""
import re
from datetime import datetime
from typing import Optional, Tuple, Any

# Current USD to INR benchmark
USD_TO_INR = 83.50
EUR_TO_INR = 90.00
GBP_TO_INR = 105.00


class JobNormalizer:
    @staticmethod
    def normalize_salary(
        salary_str: Optional[str],
        default_currency: str = "INR"
    ) -> Tuple[Optional[float], Optional[float], str]:
        """
        Parses salary string into min_annual_inr, max_annual_inr, and currency.
        Supports patterns like '$50k - $80k', '₹35,000/mo', '6 - 12 LPA', '80000 USD'.
        """
        if not salary_str or not salary_str.strip():
            return None, None, "INR"

        s = salary_str.lower().strip().replace(",", "")
        currency_multiplier = 1.0

        if "$" in s or "usd" in s:
            currency_multiplier = USD_TO_INR
        elif "€" in s or "eur" in s:
            currency_multiplier = EUR_TO_INR
        elif "£" in s or "gbp" in s:
            currency_multiplier = GBP_TO_INR

        # Check for monthly/hourly indicator
        is_monthly = "/mo" in s or "per month" in s or "monthly" in s or "pm" in s
        is_hourly = "/hr" in s or "per hour" in s or "hourly" in s
        is_lakh = "lpa" in s or "lac" in s or "lakh" in s

        # Extract numeric values
        numbers = re.findall(r"\b\d+(?:\.\d+)?(?:k)?\b", s)
        parsed_vals = []
        for n in numbers:
            mult = 1.0
            if n.endswith("k"):
                mult = 1000.0
                n = n[:-1]
            try:
                val = float(n) * mult
                if is_lakh:
                    val = val * 100000.0
                elif is_monthly:
                    val = val * 12.0
                elif is_hourly:
                    val = val * 2080.0  # standard 40 hrs/wk * 52 wks
                
                parsed_vals.append(val * currency_multiplier)
            except ValueError:
                continue

        if len(parsed_vals) == 1:
            return parsed_vals[0], parsed_vals[0], "INR"
        elif len(parsed_vals) >= 2:
            return min(parsed_vals), max(parsed_vals), "INR"

        return None, None, "INR"

    @staticmethod
    def normalize_location(location_str: Optional[str]) -> Tuple[str, bool, Optional[str], Optional[str]]:
        """
        Cleans location strings and standardizes city names.
        Returns: (normalized_location, is_remote, country, city)
        """
        if not location_str or not location_str.strip():
            return "Remote", True, None, None

        loc = location_str.strip()
        loc_lower = loc.lower()

        is_remote = any(k in loc_lower for k in ["remote", "wfh", "anywhere", "telecommute", "work from home"])

        # City mappings
        city_mapping = {
            "bengaluru": "Bangalore",
            "bangalore": "Bangalore",
            "mumbai": "Mumbai",
            "bombay": "Mumbai",
            "delhi ncr": "Delhi-NCR",
            "new delhi": "Delhi-NCR",
            "delhi": "Delhi-NCR",
            "gurugram": "Gurgaon",
            "gurgaon": "Gurgaon",
            "noida": "Noida",
            "hyderabad": "Hyderabad",
            "pune": "Pune",
            "chennai": "Chennai",
            "kolkata": "Kolkata"
        }

        detected_city = None
        for key, standard_city in city_mapping.items():
            if key in loc_lower:
                detected_city = standard_city
                break

        return loc, is_remote, ("India" if detected_city else None), detected_city

    @staticmethod
    def normalize_date(date_val: Any) -> Optional[str]:
        """
        Converts timestamp / string into ISO-8601 YYYY-MM-DD
        """
        if not date_val:
            return None
        if isinstance(date_val, (int, float)):
            try:
                # Check if in milliseconds
                if date_val > 1e11:
                    date_val = date_val / 1000.0
                return datetime.fromtimestamp(date_val).strftime("%Y-%m-%d")
            except Exception:
                return None
        
        d_str = str(date_val).strip()
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%a, %d %b %Y %H:%M:%S %z"):
            try:
                # Remove timezone subseconds if needed
                clean_s = re.sub(r"\.\d+", "", d_str).replace("Z", "")
                return datetime.strptime(clean_s, fmt).strftime("%Y-%m-%d")
            except Exception:
                continue
        
        # Fallback: regex search YYYY-MM-DD
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", d_str)
        if match:
            return match.group(1)
        return None
