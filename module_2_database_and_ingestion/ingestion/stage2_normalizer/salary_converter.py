"""
Stage 2 Normalizer: Salary Converter
Converts raw compensation strings (LPA, monthly stipends, foreign currencies)
into standardized annual INR ranges while preserving raw values.
"""
from typing import Optional, Tuple
import re
import logging

logger = logging.getLogger("SalaryConverter")

# Baseline exchange rates to INR (Cached with explicit timestamp indicator)
EXCHANGE_RATES_TO_INR = {
    "USD": 83.50,
    "EUR": 91.20,
    "GBP": 106.50,
    "CAD": 61.30,
    "AUD": 55.40,
    "SGD": 62.10,
    "AED": 22.75,
    "INR": 1.00
}


class SalaryConverter:
    """Standardizes multi-currency salaries and stipends into annual INR ranges."""

    @classmethod
    def convert(
        cls,
        raw_salary: Optional[str],
        custom_rates: Optional[dict] = None
    ) -> Tuple[Optional[float], Optional[float], str]:
        """
        Parses raw salary and returns (salary_min_annual_inr, salary_max_annual_inr, currency).
        Returns (None, None, 'INR') if salary is unknown or undisclosed.
        """
        if not raw_salary or not isinstance(raw_salary, str):
            return None, None, "INR"

        s = raw_salary.strip()
        s_lower = s.lower()

        # Check for undisclosed / not mentioned
        if any(term in s_lower for term in ["not disclosed", "undisclosed", "best in industry", "competitive", "confidential", "as per norms"]):
            return None, None, "INR"

        rates = {**EXCHANGE_RATES_TO_INR, **(custom_rates or {})}

        # Identify Currency
        currency = "INR"
        multiplier = 1.0
        if "$" in s or "usd" in s_lower:
            currency = "USD"
            multiplier = rates.get("USD", 83.5)
        elif "€" in s or "eur" in s_lower:
            currency = "EUR"
            multiplier = rates.get("EUR", 91.2)
        elif "£" in s or "gbp" in s_lower:
            currency = "GBP"
            multiplier = rates.get("GBP", 106.5)
        elif "aed" in s_lower:
            currency = "AED"
            multiplier = rates.get("AED", 22.75)
        elif "₹" in s or "rs" in s_lower or "inr" in s_lower or "lpa" in s_lower or "lac" in s_lower:
            currency = "INR"
            multiplier = 1.0

        is_monthly = any(m in s_lower for m in ["month", "pm", "p.m.", "/mo", "per month"])
        is_lpa = any(l in s_lower for l in ["lpa", "lac", "lakh", "lacs", "p.a.", "per annum"])

        # Clean digits and ranges
        # Extract numbers like 4.5, 6, 12,00,000, 35000, 80k
        clean_text = s.replace(",", "")
        numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", clean_text)]

        if not numbers:
            return None, None, "INR"

        val_min = numbers[0]
        val_max = numbers[1] if len(numbers) > 1 else val_min

        # Case 1: Indian LPA notation (e.g., 4.5 - 7.5 LPA)
        if is_lpa or (val_max <= 100.0 and currency == "INR" and not is_monthly):
            sal_min = val_min * 100000.0
            sal_max = val_max * 100000.0
        # Case 2: Foreign salary in thousands (e.g., $80k - $120k)
        elif "k" in s_lower and val_max < 1000.0:
            sal_min = val_min * 1000.0 * multiplier
            sal_max = val_max * 1000.0 * multiplier
        # Case 3: Monthly stipend / wage
        elif is_monthly:
            sal_min = val_min * 12.0 * multiplier
            sal_max = val_max * 12.0 * multiplier
        # Case 4: Full annual figure (e.g. 600000 - 900000)
        else:
            sal_min = val_min * multiplier
            sal_max = val_max * multiplier

        # Validation sanity
        if sal_min > sal_max:
            sal_min, sal_max = sal_max, sal_min

        return round(sal_min, 2), round(sal_max, 2), "INR"
