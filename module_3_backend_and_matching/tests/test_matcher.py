"""
Unit Tests for AI Matching Engine Subsystems
Tests Embedder, Rule Filter, Skill Gap Analyzer, and Match Orchestrator.
"""
import math
import pytest

from module_3_backend_and_matching.matcher.embedder import (
    generate_embedding,
    cosine_similarity
)
from module_3_backend_and_matching.matcher.rule_filter import (
    RuleFilter,
    calculate_age
)
from module_3_backend_and_matching.matcher.skill_gap_analyzer import (
    SkillGapAnalyzer,
    normalize_skill
)
from module_3_backend_and_matching.matcher.semantic_scorer import (
    SemanticScorer
)
from module_3_backend_and_matching.matcher.match_orchestrator import (
    MatchOrchestrator
)


def test_embedder_dimensions_and_normalization():
    text = "Full Stack Python FastAPI React Developer"
    emb = generate_embedding(text, dim=384)

    assert len(emb) == 384
    # Magnitude should be close to 1.0 (unit vector)
    norm = math.sqrt(sum(x * x for x in emb))
    assert abs(norm - 1.0) < 0.01


def test_cosine_similarity_properties():
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0]
    vec_c = [0.0, 1.0, 0.0]

    assert cosine_similarity(vec_a, vec_b) == 1.0
    assert cosine_similarity(vec_a, vec_c) == 0.0
    assert cosine_similarity([], vec_a) == 0.0


def test_rule_filter_batch_eligibility():
    student = {"passing_year": 2025, "open_to_internships": True, "open_to_full_time": True}
    job_eligible = {"batch_eligible": [2024, 2025], "employment_type": "full_time"}
    job_ineligible = {"batch_eligible": [2022, 2023], "employment_type": "full_time"}

    passed, reasons = RuleFilter.evaluate(student, job_eligible)
    assert passed is True
    assert len(reasons) == 0

    passed_bad, reasons_bad = RuleFilter.evaluate(student, job_ineligible)
    assert passed_bad is False
    assert any("mismatch" in r for r in reasons_bad)


def test_rule_filter_govt_age_and_relaxation():
    # 29-year old candidate
    student_obc = {
        "date_of_birth": "1997-01-01",
        "category": "OBC",
        "passing_year": 2020
    }
    student_gen = {
        "date_of_birth": "1997-01-01",
        "category": "GEN",
        "passing_year": 2020
    }

    # Govt job max age = 28 years
    govt_job = {
        "govt_metadata": {
            "age_min": 18,
            "age_max": 28
        }
    }

    # OBC has +3 years relaxation (28 + 3 = 31), so 29yo passes!
    passed_obc, _ = RuleFilter.evaluate(student_obc, govt_job)
    assert passed_obc is True

    # GEN has 0 relaxation (max 28), so 29yo fails!
    passed_gen, reasons_gen = RuleFilter.evaluate(student_gen, govt_job)
    assert passed_gen is False
    assert any("exceeds maximum limit" in r for r in reasons_gen)


def test_skill_gap_analyzer_overlap_and_recommendation():
    candidate_skills = ["Python", "FastAPI", "PostgreSQL", "Git"]
    job_skills = ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"]

    report = SkillGapAnalyzer.analyze(candidate_skills, job_skills)

    assert "python" in report["matched_skills"]
    assert "fastapi" in report["matched_skills"]
    assert "postgresql" in report["matched_skills"]
    assert "docker" in report["missing_skills"]
    assert "kubernetes" in report["missing_skills"]

    # 3 out of 5 skills matched = 60.0%
    assert report["skill_coverage_pct"] == 60.0
    assert "docker" in report["recommendation"].lower()


def test_match_orchestrator_high_match():
    student = {
        "degree": "B.Tech",
        "branch": "Computer Science",
        "cgpa": 8.5,
        "passing_year": 2025,
        "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        "preferred_roles": ["Backend Developer", "Full Stack Engineer"],
        "preferred_locations": ["Bangalore"],
        "open_to_remote": True,
        "open_to_full_time": True
    }

    job = {
        "title": "Junior Backend Developer (Python / FastAPI)",
        "company_name": "Swiggy",
        "employment_type": "full_time",
        "batch_eligible": [2024, 2025],
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "is_remote": True,
        "city": "Bangalore"
    }

    eval_result = MatchOrchestrator.match(student, job)

    assert eval_result["hard_filters_passed"] is True
    assert eval_result["match_score"] >= 80.0
    assert eval_result["match_badge"] == "High Match"
    assert "Strong alignment" in eval_result["why_matched"]
