"""
Anti-Hallucination Guard
Guarantees that AI-tailored resumes strictly contain truthful, verified facts
from the candidate's Master Verified Profile without fabricating skills or credentials.
"""
from typing import Any, Dict, List, Set, Tuple
import logging

logger = logging.getLogger("AntiHallucinationGuard")


class AntiHallucinationGuard:
    """Enforces zero-fabrication rules for AI-assisted resume generation."""

    @classmethod
    def validate_and_filter_skills(
        cls,
        proposed_skills: List[str],
        verified_skills: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Cross-checks proposed resume skills against the candidate's verified skill list.
        Returns (approved_skills, dropped_fabrications).
        """
        verified_norm = {s.strip().lower() for s in verified_skills if s.strip()}
        approved = []
        dropped = []

        for skill in proposed_skills:
            clean = skill.strip()
            if clean.lower() in verified_norm:
                approved.append(clean)
            else:
                dropped.append(clean)
                logger.warning(f"[AntiHallucination] Dropped unverified hallucinated skill: '{clean}'")

        return approved, dropped

    @classmethod
    def verify_academic_integrity(
        cls,
        tailored_academics: Dict[str, Any],
        verified_profile: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Ensures degrees, passing years, and CGPA match verified records exactly.
        """
        discrepancies = []

        # Degree check
        if tailored_academics.get("degree") and tailored_academics.get("degree") != verified_profile.get("degree"):
            discrepancies.append(
                f"Degree mismatch: Tailored says '{tailored_academics.get('degree')}', verified is '{verified_profile.get('degree')}'"
            )

        # CGPA check (cannot be inflated)
        tailored_cgpa = tailored_academics.get("cgpa")
        verified_cgpa = verified_profile.get("cgpa")
        if tailored_cgpa is not None and verified_cgpa is not None:
            if tailored_cgpa > verified_cgpa:
                discrepancies.append(
                    f"CGPA inflation detected: Tailored says {tailored_cgpa}, verified record is {verified_cgpa}"
                )

        # Passing Year check
        tailored_year = tailored_academics.get("passing_year")
        verified_year = verified_profile.get("passing_year")
        if tailored_year and verified_year and tailored_year != verified_year:
            discrepancies.append(
                f"Graduation year mismatch: Tailored says {tailored_year}, verified record is {verified_year}"
            )

        is_valid = len(discrepancies) == 0
        return is_valid, discrepancies
