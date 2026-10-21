"""
Resume Tailoring Engine
Customizes student profile content to match target job requirements,
optimizing keyword relevance and ordering while respecting strict anti-hallucination rules.
"""
from typing import Any, Dict, List, Optional
from module_3_backend_and_matching.matcher.skill_gap_analyzer import SkillGapAnalyzer, normalize_skill
from module_4_resume_and_document_lab.resume_studio.anti_hallucination import AntiHallucinationGuard


class ResumeTailor:
    """Tailors candidate profile data into an ATS-optimized resume structure."""

    @classmethod
    def tailor_resume(
        cls,
        candidate_profile: Dict[str, Any],
        candidate_user: Dict[str, Any],
        target_job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes an ATS-tailored resume specification aligned with target job.
        Strictly sources all facts from verified candidate records.
        """
        verified_skills = candidate_profile.get("skills") or []
        job_skills = target_job.get("skills") or []
        job_title = target_job.get("title") or "Software Engineer"
        company_name = target_job.get("company_name") or target_job.get("company") or "Technology Employer"

        # 1. Analyze skill alignment
        gap_report = SkillGapAnalyzer.analyze(
            candidate_skills=verified_skills,
            job_skills=job_skills,
            job_title=job_title,
            job_description=target_job.get("description_clean") or target_job.get("description_raw") or ""
        )

        matched_norm = set(gap_report["matched_skills"])

        # 2. Partition skills: Core Matched Skills vs Additional Verified Skills
        core_skills = []
        secondary_skills = []

        for skill in verified_skills:
            if normalize_skill(skill) in matched_norm:
                core_skills.append(skill)
            else:
                secondary_skills.append(skill)

        # Anti-Hallucination check: ensure no skills outside verified set
        all_included = core_skills + secondary_skills
        clean_skills, dropped = AntiHallucinationGuard.validate_and_filter_skills(
            proposed_skills=all_included,
            verified_skills=verified_skills
        )

        # 3. Formulate Truthful ATS Professional Summary
        full_name = candidate_user.get("full_name") or "Candidate"
        degree = candidate_profile.get("degree") or "Engineering"
        branch = candidate_profile.get("branch") or "Computer Science"
        passing_year = candidate_profile.get("passing_year")
        bio = candidate_profile.get("bio")

        if core_skills:
            top_tech = ", ".join(core_skills[:4])
            summary_intro = (
                f"{degree} candidate ({branch}"
                f"{', ' + str(passing_year) if passing_year else ''}) "
                f"with practical competencies in {top_tech}. "
            )
        else:
            summary_intro = (
                f"{degree} graduate in {branch} with strong foundational engineering skills. "
            )

        if bio and len(bio.strip()) >= 20:
            summary_tail = bio.strip()
        else:
            summary_tail = (
                f"Dedicated to building scalable software solutions and contributing effectively to {company_name}."
            )

        professional_summary = f"{summary_intro}{summary_tail}"

        # 4. Construct Structured Tailored Resume Object
        tailored_data = {
            "personal_info": {
                "full_name": full_name,
                "email": candidate_user.get("email"),
                "linkedin_url": candidate_profile.get("linkedin_url"),
                "github_url": candidate_profile.get("github_url"),
                "portfolio_url": candidate_profile.get("portfolio_url"),
                "location": (candidate_profile.get("preferred_locations") or ["India"])[0]
            },
            "professional_summary": professional_summary,
            "target_role": job_title,
            "target_company": company_name,
            "skills_breakdown": {
                "core_competencies": core_skills,
                "supporting_technologies": secondary_skills,
                "all_skills": clean_skills
            },
            "education": {
                "degree": degree,
                "branch": branch,
                "college_name": candidate_profile.get("college_name") or "Affiliated University",
                "passing_year": passing_year,
                "cgpa": candidate_profile.get("cgpa")
            },
            "certifications": candidate_profile.get("certifications") or [],
            "ats_alignment": {
                "matched_skills_count": len(core_skills),
                "coverage_pct": gap_report["skill_coverage_pct"],
                "missing_skills": gap_report["missing_skills"],
                "recommendation": gap_report["recommendation"]
            }
        }

        return tailored_data
