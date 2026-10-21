"""
Match Orchestrator
Master scoring coordinator combining Hard Rule Filters, Skill Gap Analysis,
Semantic Vector Similarity, and Role/Location Preferences into a unified hybrid score.
"""
from typing import Any, Dict, List
from module_3_backend_and_matching.config import settings
from module_3_backend_and_matching.matcher.rule_filter import RuleFilter
from module_3_backend_and_matching.matcher.skill_gap_analyzer import SkillGapAnalyzer
from module_3_backend_and_matching.matcher.semantic_scorer import SemanticScorer


class MatchOrchestrator:
    """Coordinates hybrid multi-factor matching for candidate-job pairs."""

    @classmethod
    def evaluate_preferences(
        cls,
        student_profile: Dict[str, Any],
        job: Dict[str, Any]
    ) -> float:
        """
        Scores alignment between candidate preferences (roles, locations, remote) and job details.
        Returns score from 0.0 to 100.0.
        """
        score = 50.0  # Base neutral score

        job_title = (job.get("title") or "").lower()
        pref_roles = [r.lower() for r in (student_profile.get("preferred_roles") or [])]
        if pref_roles:
            if any(role in job_title or job_title in role for role in pref_roles):
                score += 30.0
            else:
                score -= 10.0

        # Location / Remote
        is_job_remote = job.get("is_remote", False)
        open_to_remote = student_profile.get("open_to_remote", True)
        pref_locs = [loc.lower() for loc in (student_profile.get("preferred_locations") or [])]
        job_city = (job.get("city") or "").lower()

        if is_job_remote and open_to_remote:
            score += 20.0
        elif pref_locs and job_city and any(p in job_city or job_city in p for p in pref_locs):
            score += 20.0

        return max(0.0, min(100.0, score))

    @classmethod
    def match(
        cls,
        student_profile: Dict[str, Any],
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Performs full hybrid evaluation for a student profile and a job listing.
        Returns match card metadata including score %, badge, skill gaps, and explanations.
        """
        # 1. Hard Rule Eligibility
        hard_passed, failure_reasons = RuleFilter.evaluate(student_profile, job)

        # 2. Skill Gap Analysis
        candidate_skills = student_profile.get("skills") or []
        job_skills = job.get("skills") or []
        job_title = job.get("title") or ""
        job_desc = job.get("description_clean") or job.get("description_raw") or ""

        skill_gap = SkillGapAnalyzer.analyze(
            candidate_skills=candidate_skills,
            job_skills=job_skills,
            job_title=job_title,
            job_description=job_desc
        )

        # 3. Semantic Vector Similarity
        semantic_sim = SemanticScorer.score(student_profile, job)
        semantic_score_pct = round(semantic_sim * 100.0, 1)

        # In offline/fallback mode where bag-of-words projection is used,
        # ensure high technical skill alignment appropriately elevates the semantic factor
        if skill_gap["skill_coverage_pct"] >= 75.0:
            effective_semantic = max(semantic_score_pct, skill_gap["skill_coverage_pct"] * 0.8)
        else:
            effective_semantic = semantic_score_pct

        # 4. Preference Alignment
        pref_score = cls.evaluate_preferences(student_profile, job)

        # 5. Hybrid Weighted Score
        hybrid_score = (
            settings.WEIGHT_SKILL_OVERLAP * skill_gap["skill_coverage_pct"] +
            settings.WEIGHT_SEMANTIC_SIMILARITY * effective_semantic +
            settings.WEIGHT_PREFERENCES * pref_score
        )

        # Apply hard gate penalty if hard filters failed
        if not hard_passed:
            final_score = min(35.0, round(hybrid_score * 0.4, 1))
        else:
            final_score = round(max(0.0, min(100.0, hybrid_score)), 1)

        # 6. Assign Match Badge
        if final_score >= settings.HIGH_MATCH_THRESHOLD:
            badge = "High Match"
        elif final_score >= settings.GOOD_MATCH_THRESHOLD:
            badge = "Good Match"
        elif final_score >= settings.DEFAULT_MIN_MATCH_SCORE:
            badge = "Fair Match"
        else:
            badge = "Low Match"

        # 7. Natural Language Explanation
        matched_cnt = len(skill_gap["matched_skills"])
        total_req = matched_cnt + len(skill_gap["missing_skills"])

        if hard_passed and final_score >= settings.GOOD_MATCH_THRESHOLD:
            if matched_cnt > 0:
                top_skills = ", ".join(skill_gap["matched_skills"][:3])
                why_matched = (
                    f"Strong alignment: You match {matched_cnt}/{total_req} key competencies ({top_skills}) "
                    f"and meet all eligibility criteria."
                )
            else:
                why_matched = f"Strong semantic alignment with role requirements and candidate preferences."
        elif not hard_passed:
            why_matched = f"Ineligible: {'; '.join(failure_reasons)}."
        else:
            why_matched = f"Moderate match: Skill coverage is {skill_gap['skill_coverage_pct']}%. Upskilling recommended."

        return {
            "match_score": final_score,
            "match_badge": badge,
            "hard_filters_passed": hard_passed,
            "disqualification_reasons": failure_reasons,
            "skill_gap": skill_gap,
            "why_matched": why_matched,
            "semantic_score_pct": semantic_score_pct,
            "preference_score": pref_score
        }
