"""
Unit Tests for Student Profile and Completeness
Tests completeness percentage scoring logic and profile schema validation.
"""
from module_3_backend_and_matching.models.student_profile import StudentProfile
from module_3_backend_and_matching.routes.profile_routes import calculate_completeness


def test_profile_completeness_calculation():
    # Empty profile
    p1 = StudentProfile(user_id="u1")
    assert calculate_completeness(p1) == 0.0

    # Profile with academics
    p2 = StudentProfile(
        user_id="u2",
        degree="B.Tech",
        branch="Computer Science",
        passing_year=2025,
        cgpa=8.2
    )
    score_p2 = calculate_completeness(p2)
    assert score_p2 == 30.0  # 10 + 10 + 5 + 5

    # Full profile
    p3 = StudentProfile(
        user_id="u3",
        degree="B.Tech",
        branch="Computer Science",
        passing_year=2025,
        cgpa=8.5,
        skills=["Python", "FastAPI", "React", "Docker", "PostgreSQL"],
        bio="Passionate software engineer focused on distributed systems and APIs.",
        preferred_roles=["Backend Developer"],
        preferred_locations=["Bangalore"],
        github_url="https://github.com/candidate",
        linkedin_url="https://linkedin.com/in/candidate",
        date_of_birth="2002-05-15"
    )
    score_p3 = calculate_completeness(p3)
    assert score_p3 >= 90.0
