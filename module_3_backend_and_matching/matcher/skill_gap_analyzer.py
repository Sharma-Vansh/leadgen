"""
Skill Gap Analysis Engine
Analyzes overlap between candidate competencies and job requirements,
extracts missing skills, calculates skill coverage, and formulates upskilling recommendations.
"""
import re
from typing import Any, Dict, List, Set, Tuple

# Canonical Synonym Map for Tech Skills
SKILL_SYNONYMS: Dict[str, str] = {
    "reactjs": "react",
    "react.js": "react",
    "nextjs": "next.js",
    "next.js": "next.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "angularjs": "angular",
    "angular.js": "angular",
    "nodejs": "node.js",
    "node.js": "node.js",
    "expressjs": "express.js",
    "fastapi": "fastapi",
    "django": "django",
    "flask": "flask",
    "spring boot": "spring boot",
    "springboot": "spring boot",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mysql": "mysql",
    "mongodb": "mongodb",
    "redis": "redis",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "docker": "docker",
    "aws": "aws",
    "gcp": "gcp",
    "azure": "azure",
    "git": "git",
    "github": "github",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "linux": "linux",
    "python": "python",
    "py": "python",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "c++": "c++",
    "cpp": "c++",
    "golang": "go",
    "go": "go",
    "java": "java",
    "c#": "c#",
    "csharp": "c#",
    "sql": "sql",
    "nosql": "nosql",
    "graphql": "graphql",
    "rest": "rest api",
    "rest api": "rest api",
    "restful": "rest api",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "artificial intelligence": "ai",
    "ai": "ai",
    "deep learning": "deep learning",
    "nlp": "nlp",
    "llm": "llm",
    "llms": "llm",
    "langchain": "langchain",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "html": "html",
    "css": "css",
    "tailwind": "tailwindcss",
    "tailwindcss": "tailwindcss",
}


def normalize_skill(skill: str) -> str:
    """Normalizes skill string to lowercase canonical token."""
    cleaned = re.sub(r"[^\w\s\+\#\./\-]", "", skill.strip().lower())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return SKILL_SYNONYMS.get(cleaned, cleaned)


class SkillGapAnalyzer:
    """Evaluates candidate skills against job required skills."""

    @classmethod
    def analyze(
        cls,
        candidate_skills: List[str],
        job_skills: List[str],
        job_title: str = "",
        job_description: str = ""
    ) -> Dict[str, Any]:
        """
        Analyzes overlap and generates skill gap metrics.
        Returns:
            matched_skills: List[str]
            missing_skills: List[str]
            skill_coverage_pct: float (0.0 to 100.0)
            recommendation: str
        """
        cand_norm_set: Set[str] = {normalize_skill(s) for s in candidate_skills if s.strip()}
        job_norm_set: Set[str] = {normalize_skill(s) for s in job_skills if s.strip()}

        # Also extract common skills mentioned in job title/description if job_skills is sparse
        if len(job_norm_set) < 3 and (job_title or job_description):
            combined_text = f"{job_title} {job_description}".lower()
            for key, canonical in SKILL_SYNONYMS.items():
                if len(key) >= 3 and re.search(r"\b" + re.escape(key) + r"\b", combined_text):
                    job_norm_set.add(canonical)

        if not job_norm_set:
            # If job has no listed skills, coverage is neutral (75%)
            return {
                "matched_skills": sorted(list(cand_norm_set)),
                "missing_skills": [],
                "skill_coverage_pct": 75.0,
                "recommendation": "No specific technical stack specified by employer."
            }

        matched_set = cand_norm_set.intersection(job_norm_set)
        missing_set = job_norm_set - cand_norm_set

        coverage_pct = round((len(matched_set) / len(job_norm_set)) * 100.0, 1)

        # Build recommendation
        if not missing_set:
            recommendation = "You have 100% skill coverage for this opening! Apply now."
        elif len(missing_set) <= 2:
            missing_str = ", ".join(sorted(list(missing_set)))
            recommendation = f"Strong fit! Upskilling in {missing_str} will make your application stand out."
        else:
            top_missing = sorted(list(missing_set))[:3]
            missing_str = ", ".join(top_missing)
            recommendation = f"Target {missing_str} projects to dramatically boost your interview callback rate."

        return {
            "matched_skills": sorted(list(matched_set)),
            "missing_skills": sorted(list(missing_set)),
            "skill_coverage_pct": coverage_pct,
            "recommendation": recommendation
        }
