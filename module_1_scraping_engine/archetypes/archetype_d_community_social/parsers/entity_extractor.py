"""
Archetype D, Tier 2: Entity Extractor
Uses structured regex and NLP heuristics to extract:
- Company Name
- Role & Tech Stack
- Salary / Stipend (e.g. ₹35,000/month, 8-12 LPA)
- Target Batch (2024, 2025, 2026 graduates)
- Location & Work Mode
"""
import re
from typing import Dict, Any, List, Optional
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer


class EntityExtractor:
    BATCH_REGEX = re.compile(r"\b(202[3-7])\s*(?:batch|passout|graduates|passouts)?\b", re.IGNORECASE)
    STIPEND_REGEX = re.compile(
        r"(?:stipend|salary|ctc|package|pay)\s*[:\-]?\s*([₹$€£]?\s*\d+(?:[\d,.]*)?\s*(?:k|lpa|pm|per month|monthly|usd)?)",
        re.IGNORECASE
    )
    ROLE_REGEX = re.compile(
        r"\b((?:frontend|backend|fullstack|full-stack|software|sde|ai/ml|machine learning|data science|data analyst|devops|cloud|react|python|qa)\s*(?:engineer|developer|intern|trainee|analyst|associate)?)\b",
        re.IGNORECASE
    )
    COMPANY_REGEX = re.compile(
        r"(?:hiring at|company|organisation|hiring for)\s*[:\-]?\s*([A-Za-z0-9\s&]+?)(?:\n|,|\.|\s-|\sfor|\srole)",
        re.IGNORECASE
    )

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        result = {
            "company": "Startup / Direct Hiring",
            "role": "Software Developer",
            "batch_eligible": [],
            "salary_raw": None,
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "INR",
            "skills": []
        }

        # 1. Batch extraction
        batch_matches = cls.BATCH_REGEX.findall(text)
        if batch_matches:
            result["batch_eligible"] = sorted(list(set(int(b) for b in batch_matches)))

        # 2. Salary / Stipend extraction
        stipend_match = cls.STIPEND_REGEX.search(text)
        if stipend_match:
            sal_str = stipend_match.group(1).strip()
            result["salary_raw"] = sal_str
            s_min, s_max, curr = JobNormalizer.normalize_salary(sal_str)
            result["salary_min"] = s_min
            result["salary_max"] = s_max
            result["salary_currency"] = curr

        # 3. Role extraction
        role_match = cls.ROLE_REGEX.search(text)
        if role_match:
            result["role"] = role_match.group(1).strip().title()

        # 4. Company extraction
        comp_match = cls.COMPANY_REGEX.search(text)
        if comp_match:
            cand = comp_match.group(1).strip()
            if 2 < len(cand) < 30:
                result["company"] = cand

        # 5. Skills extraction
        known_tech = ["Python", "Java", "C++", "React", "Node.js", "Django", "FastAPI", "SQL", "PostgreSQL", "MongoDB", "AWS", "Docker", "Git"]
        for tech in known_tech:
            if re.search(r"\b" + re.escape(tech) + r"\b", text, re.IGNORECASE):
                result["skills"].append(tech)

        return result
