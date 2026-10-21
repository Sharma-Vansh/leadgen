"""
ATS Readability & Compliance Scorer
Evaluates resume parseability, section header standardization, keyword coverage,
and ATS scanner friendliness (Workday, Greenhouse, Lever, Taleo).
"""
from typing import Any, Dict, List, Optional, Tuple


class ATSScorer:
    """Calculates ATS readability score (0 to 100) and actionable diagnostics."""

    @classmethod
    def score_resume(
        cls,
        resume_data: Dict[str, Any],
        job_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculates ATS compatibility score and section diagnostics.
        """
        score = 0.0
        breakdown = {}
        tips = []

        # 1. Contact Information Completeness (25 points)
        personal = resume_data.get("personal_info") or {}
        contact_score = 0.0
        if personal.get("full_name"):
            contact_score += 10.0
        if personal.get("email") and "@" in personal.get("email"):
            contact_score += 10.0
        if personal.get("linkedin_url") or personal.get("github_url"):
            contact_score += 5.0
        else:
            tips.append("Add a LinkedIn or GitHub profile link for technical recruiter verification.")

        score += contact_score
        breakdown["contact_info"] = contact_score

        # 2. Standardized Section Headers (25 points)
        section_score = 0.0
        if resume_data.get("professional_summary"):
            section_score += 7.0
        else:
            tips.append("Include a concise 2-sentence Professional Summary targeted to the role.")

        if resume_data.get("education"):
            section_score += 8.0

        skills_dict = resume_data.get("skills_breakdown") or {}
        all_skills = skills_dict.get("all_skills") or []
        if len(all_skills) >= 3:
            section_score += 10.0
        elif len(all_skills) > 0:
            section_score += 5.0
            tips.append("List at least 5 technical competencies in the Skills section.")
        else:
            tips.append("Add a dedicated Technical Skills section with categorized competencies.")

        score += section_score
        breakdown["sections"] = section_score

        # 3. Keyword & Skill Alignment (35 points)
        alignment = resume_data.get("ats_alignment") or {}
        coverage_pct = alignment.get("coverage_pct", 50.0)
        keyword_score = round((coverage_pct / 100.0) * 35.0, 1)
        score += keyword_score
        breakdown["keyword_alignment"] = keyword_score

        if coverage_pct < 60.0:
            missing = alignment.get("missing_skills") or []
            if missing:
                top_m = ", ".join(missing[:3])
                tips.append(f"Consider acquiring experience in {top_m} to improve keyword relevance.")

        # 4. Single-Column ATS Format Compliance (15 points)
        format_score = 15.0
        # Single column layout has no table nesting penalty
        score += format_score
        breakdown["format_parseability"] = format_score

        final_score = round(min(100.0, max(0.0, score)), 1)

        grade = "A+" if final_score >= 90 else "A" if final_score >= 80 else "B" if final_score >= 70 else "C"

        return {
            "ats_score": final_score,
            "grade": grade,
            "breakdown": breakdown,
            "tips": tips,
            "is_ats_compliant": final_score >= 75.0
        }
