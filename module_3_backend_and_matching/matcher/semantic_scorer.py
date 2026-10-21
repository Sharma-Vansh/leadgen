"""
Semantic Vector Scorer
Calculates dense embedding cosine similarity between candidate profiles and job listings.
"""
from typing import Any, Dict, List, Optional
from module_3_backend_and_matching.matcher.embedder import generate_embedding, cosine_similarity


class SemanticScorer:
    """Computes semantic dense vector similarity between student profile and job."""

    @classmethod
    def build_student_profile_text(cls, profile: Dict[str, Any]) -> str:
        """Formats student profile into a rich contextual document for semantic embedding."""
        parts = []
        degree = profile.get("degree")
        branch = profile.get("branch")
        if degree or branch:
            parts.append(f"Education: {degree or ''} in {branch or ''}")

        skills = profile.get("skills") or []
        if skills:
            parts.append(f"Skills: {', '.join(skills)}")

        pref_roles = profile.get("preferred_roles") or []
        if pref_roles:
            parts.append(f"Target Roles: {', '.join(pref_roles)}")

        bio = profile.get("bio")
        if bio:
            parts.append(f"Bio: {bio}")

        return " | ".join(parts) if parts else "Student seeking software engineering internship"

    @classmethod
    def build_job_text(cls, job: Dict[str, Any]) -> str:
        """Formats job record into a rich contextual document for semantic embedding."""
        parts = []
        title = job.get("title")
        company = job.get("company_name") or job.get("company")
        if title:
            parts.append(f"Title: {title}")
        if company:
            parts.append(f"Company: {company}")

        skills = job.get("skills") or []
        if skills:
            parts.append(f"Skills: {', '.join(skills)}")

        desc = job.get("description_clean") or job.get("description_raw") or ""
        if desc:
            # First 500 chars of description
            parts.append(f"Summary: {desc[:500]}")

        return " | ".join(parts) if parts else (title or "Software Developer")

    @classmethod
    def score(
        cls,
        student_profile: Dict[str, Any],
        job: Dict[str, Any]
    ) -> float:
        """
        Returns cosine similarity float in range [0.0, 1.0].
        Reuses cached embeddings if present.
        """
        student_emb = student_profile.get("embedding")
        if not student_emb:
            student_text = cls.build_student_profile_text(student_profile)
            student_emb = generate_embedding(student_text)

        job_emb = job.get("embedding")
        if not job_emb:
            job_text = cls.build_job_text(job)
            job_emb = generate_embedding(job_text)

        return cosine_similarity(student_emb, job_emb)
