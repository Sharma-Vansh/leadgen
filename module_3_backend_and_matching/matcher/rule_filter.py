"""
Hard Eligibility Rules Filter
Evaluates hard criteria: Graduation batch, CGPA cutoffs, employment modality,
and government recruitment age limits with statutory category relaxations.
"""
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any


def calculate_age(dob_str: Optional[str]) -> Optional[int]:
    """Calculates age in years from ISO date string (YYYY-MM-DD)."""
    if not dob_str:
        return None
    try:
        birth_date = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except Exception:
        return None


class RuleFilter:
    """Evaluates non-negotiable hard eligibility criteria between student and job."""

    @classmethod
    def evaluate(
        cls,
        student_profile: Dict[str, Any],
        job: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Returns (is_passed: bool, disqualification_reasons: List[str]).
        """
        reasons = []

        # 1. Graduation Batch / Passing Year Check
        batch_eligible = job.get("batch_eligible") or []
        student_passing_year = student_profile.get("passing_year")
        if batch_eligible and student_passing_year:
            # If job specifies batches, student must belong to one of them
            if student_passing_year not in batch_eligible:
                reasons.append(
                    f"Graduation batch mismatch: Job requires {batch_eligible}, candidate is {student_passing_year}"
                )

        # 2. Employment Type Preference
        job_type = (job.get("employment_type") or "full_time").lower()
        open_to_internships = student_profile.get("open_to_internships", True)
        open_to_full_time = student_profile.get("open_to_full_time", True)

        if "intern" in job_type and not open_to_internships:
            reasons.append("Candidate is not open to internships")
        elif "full" in job_type and not open_to_full_time:
            reasons.append("Candidate is not open to full-time roles")

        # 3. CGPA Hard Cutoff (if job specifies min_cgpa in metadata)
        job_min_cgpa = job.get("min_cgpa")
        student_cgpa = student_profile.get("cgpa")
        if job_min_cgpa and student_cgpa:
            if student_cgpa < job_min_cgpa:
                reasons.append(
                    f"CGPA below minimum cutoff: Required {job_min_cgpa}, candidate has {student_cgpa}"
                )

        # 4. Government / PSU Age Limits & Statutory Category Relaxation
        govt_meta = job.get("govt_metadata") or {}
        if govt_meta:
            age_min = govt_meta.get("age_min")
            age_max = govt_meta.get("age_max")
            student_dob = student_profile.get("date_of_birth")
            candidate_age = calculate_age(student_dob)

            if candidate_age is not None:
                category = (student_profile.get("category") or "GEN").upper()
                # Category age relaxations (India standard)
                relaxation = 0
                if category == "OBC":
                    relaxation = 3
                elif category in ("SC", "ST"):
                    relaxation = 5
                elif category == "EWS":
                    relaxation = 0

                effective_max = (age_max + relaxation) if age_max else None

                if age_min and candidate_age < age_min:
                    reasons.append(
                        f"Age below minimum requirement: Minimum {age_min} years, candidate is {candidate_age}"
                    )
                if effective_max and candidate_age > effective_max:
                    reasons.append(
                        f"Age exceeds maximum limit: Allowed {effective_max} years (including {relaxation}yr {category} relaxation), candidate is {candidate_age}"
                    )

        # 5. Strict Location / Remote Preference
        is_job_remote = job.get("is_remote", False)
        open_to_remote = student_profile.get("open_to_remote", True)
        pref_locations = [loc.lower() for loc in (student_profile.get("preferred_locations") or [])]
        job_city = (job.get("city") or "").lower()

        if pref_locations and not is_job_remote:
            if not open_to_remote and is_job_remote:
                reasons.append("Candidate does not prefer remote work")
            elif pref_locations and job_city and not any(pref in job_city or job_city in pref for pref in pref_locations):
                # We treat location mismatch as soft unless student explicitly restricts
                pass

        is_passed = len(reasons) == 0
        return is_passed, reasons
