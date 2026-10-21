"""
Unit Tests for Anti-Hallucination Guard
Verifies that fabricated skills, altered degrees, and inflated CGPAs are strictly detected and eliminated.
"""
from module_4_resume_and_document_lab.resume_studio.anti_hallucination import AntiHallucinationGuard


def test_unverified_skills_are_dropped():
    verified_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    # AI proposed an invented skill "Rust" and "Solidity" that candidate never studied
    proposed_skills = ["Python", "FastAPI", "Rust", "Solidity", "PostgreSQL"]

    approved, dropped = AntiHallucinationGuard.validate_and_filter_skills(
        proposed_skills=proposed_skills,
        verified_skills=verified_skills
    )

    assert "Rust" in dropped
    assert "Solidity" in dropped
    assert "Python" in approved
    assert "FastAPI" in approved
    assert "PostgreSQL" in approved
    assert len(approved) == 3


def test_academic_inflation_detection():
    verified_profile = {
        "degree": "B.Tech",
        "cgpa": 7.8,
        "passing_year": 2025
    }

    # Inflated CGPA to 9.2
    inflated_tailored = {
        "degree": "B.Tech",
        "cgpa": 9.2,
        "passing_year": 2025
    }

    is_valid, discrepancies = AntiHallucinationGuard.verify_academic_integrity(
        tailored_academics=inflated_tailored,
        verified_profile=verified_profile
    )

    assert is_valid is False
    assert any("inflation detected" in d for d in discrepancies)


def test_academic_degree_mismatch_detection():
    verified_profile = {"degree": "BCA", "cgpa": 8.0, "passing_year": 2024}
    altered_tailored = {"degree": "B.Tech", "cgpa": 8.0, "passing_year": 2024}

    is_valid, discrepancies = AntiHallucinationGuard.verify_academic_integrity(
        tailored_academics=altered_tailored,
        verified_profile=verified_profile
    )

    assert is_valid is False
    assert any("Degree mismatch" in d for d in discrepancies)
