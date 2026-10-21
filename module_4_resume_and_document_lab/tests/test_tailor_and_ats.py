"""
Unit Tests for Resume Tailoring and ATS Scoring Engine
Tests core vs supporting skill partitioning, truthful summary generation, and ATS readability grading.
"""
from module_4_resume_and_document_lab.resume_studio.tailor import ResumeTailor
from module_4_resume_and_document_lab.resume_studio.ats_scorer import ATSScorer


def test_resume_tailoring_aligns_with_job():
    candidate_profile = {
        "degree": "B.Tech",
        "branch": "Computer Science",
        "college_name": "Delhi Technological University",
        "cgpa": 8.5,
        "passing_year": 2025,
        "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Git", "Java"],
        "preferred_locations": ["Bangalore"],
        "bio": "Enthusiastic developer who builds scalable microservices and web APIs."
    }

    candidate_user = {
        "id": "u-001",
        "full_name": "Aman Verma",
        "email": "aman.verma@dtu.ac.in"
    }

    target_job = {
        "title": "Backend Engineering Intern",
        "company_name": "PhonePe",
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
        "description_clean": "Looking for backend engineers skilled in Python, FastAPI, and relational databases."
    }

    tailored = ResumeTailor.tailor_resume(
        candidate_profile=candidate_profile,
        candidate_user=candidate_user,
        target_job=target_job
    )

    # Core competencies should feature the matching skills first
    core = tailored["skills_breakdown"]["core_competencies"]
    assert "Python" in core
    assert "FastAPI" in core
    assert "Docker" in core
    assert "PostgreSQL" in core

    # Java is supporting, not part of core target requirements
    supporting = tailored["skills_breakdown"]["supporting_technologies"]
    assert "Java" in supporting

    # Check ATS summary is truthful
    assert "B.Tech candidate" in tailored["professional_summary"]
    assert "Python" in tailored["professional_summary"]
    assert tailored["target_company"] == "PhonePe"


def test_ats_scorer_grading():
    resume_data = {
        "personal_info": {
            "full_name": "Aman Verma",
            "email": "aman@dtu.ac.in",
            "linkedin_url": "https://linkedin.com/in/aman",
            "github_url": "https://github.com/aman",
            "location": "Bangalore, India"
        },
        "professional_summary": "B.Tech Computer Science graduate specializing in Python APIs.",
        "education": {
            "degree": "B.Tech",
            "branch": "Computer Science",
            "college_name": "DTU",
            "passing_year": 2025,
            "cgpa": 8.5
        },
        "skills_breakdown": {
            "all_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "React"]
        },
        "ats_alignment": {
            "coverage_pct": 85.0,
            "missing_skills": []
        }
    }

    report = ATSScorer.score_resume(resume_data)

    assert report["ats_score"] >= 80.0
    assert report["grade"] in ("A", "A+")
    assert report["is_ats_compliant"] is True
    assert "contact_info" in report["breakdown"]
