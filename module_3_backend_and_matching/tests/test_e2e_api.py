"""
End-to-End REST API Integration Tests
Tests registration, JWT authentication, profile updating, and AI matched job feed retrieval.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from module_2_database_and_ingestion.db.base import Base
from module_2_database_and_ingestion.db.models.job import Job
from module_2_database_and_ingestion.db.models.company import Company
from module_2_database_and_ingestion.db.models.job_source import JobSource
import module_3_backend_and_matching.models
from module_3_backend_and_matching.main import app
from module_3_backend_and_matching.auth.dependencies import get_db


@pytest_asyncio.fixture
async def test_db_session():
    """Provides an isolated in-memory database session for API testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_full_student_journey_api_e2e(test_db_session):
    # Override get_db dependency to point to in-memory test database
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register candidate student
        reg_payload = {
            "email": "priya.sharma@college.ac.in",
            "password": "StrongStudentPassword#2026",
            "full_name": "Priya Sharma",
            "role": "student"
        }
        reg_resp = await client.post("/auth/register", json=reg_payload)
        assert reg_resp.status_code == 201, reg_resp.text
        reg_data = reg_resp.json()
        assert "access_token" in reg_data
        token = reg_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Login verification
        login_resp = await client.post("/auth/login", json={
            "email": "priya.sharma@college.ac.in",
            "password": "StrongStudentPassword#2026"
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

        # 3. Get /auth/me
        me_resp = await client.get("/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "priya.sharma@college.ac.in"

        # 4. Update Student Profile
        profile_payload = {
            "degree": "B.Tech",
            "branch": "Computer Science & Engineering",
            "cgpa": 8.8,
            "passing_year": 2025,
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
            "preferred_roles": ["Backend Developer", "Full Stack Engineer"],
            "preferred_locations": ["Bangalore", "Pune"],
            "open_to_remote": True,
            "open_to_full_time": True,
            "bio": "Enthusiastic developer who builds scalable REST APIs with Python & FastAPI."
        }
        prof_resp = await client.put("/api/student/profile", json=profile_payload, headers=headers)
        assert prof_resp.status_code == 200, prof_resp.text
        prof_data = prof_resp.json()
        assert prof_data["degree"] == "B.Tech"
        assert prof_data["profile_completeness_pct"] >= 70.0

        # 5. Populate Test Companies and Jobs into database
        company = Company(name="Swiggy", domain="swiggy.in")
        source = JobSource(source_id="SRC-0036", source_name="Remotive", archetype="A")
        test_db_session.add_all([company, source])
        await test_db_session.flush()

        # Job 1: High Match (Python + FastAPI + 2025 Batch)
        job1 = Job(
            company_id=company.id,
            source_id=source.source_id,
            title="Junior Backend Engineer (Python / FastAPI)",
            skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
            batch_eligible=[2024, 2025],
            city="Bangalore",
            is_remote=True,
            employment_type="full_time",
            salary_min=1200000.0,
            salary_max=1800000.0,
            apply_url="https://swiggy.in/careers/job-001",
            status="active"
        )

        # Job 2: Partial Match (Java + Spring Boot)
        job2 = Job(
            company_id=company.id,
            source_id=source.source_id,
            title="Java Enterprise Developer",
            skills=["Java", "Spring Boot", "Microservices"],
            batch_eligible=[2024, 2025],
            city="Hyderabad",
            is_remote=False,
            employment_type="full_time",
            salary_min=800000.0,
            salary_max=1200000.0,
            apply_url="https://swiggy.in/careers/job-002",
            status="active"
        )

        # Job 3: Ineligible Batch (2020 Batch Only)
        job3 = Job(
            company_id=company.id,
            source_id=source.source_id,
            title="Senior Architect (Python)",
            skills=["Python", "Distributed Systems"],
            batch_eligible=[2019, 2020],
            city="Bangalore",
            is_remote=True,
            employment_type="full_time",
            apply_url="https://swiggy.in/careers/job-003",
            status="active"
        )

        test_db_session.add_all([job1, job2, job3])
        await test_db_session.commit()

        # 6. Fetch Matched Job Feed via API
        feed_resp = await client.get("/api/jobs/matched-feed?only_eligible=true", headers=headers)
        assert feed_resp.status_code == 200, feed_resp.text
        feed_data = feed_resp.json()

        # Job 3 should be filtered out by only_eligible=True because 2025 != [2019, 2020]
        assert feed_data["total_matches"] == 2
        items = feed_data["items"]
        assert len(items) == 2

        # Job 1 (Python / FastAPI) MUST rank #1 with High Match
        top_job = items[0]
        assert top_job["title"] == "Junior Backend Engineer (Python / FastAPI)"
        assert top_job["match_score"] >= 80.0
        assert top_job["match_badge"] == "High Match"
        assert top_job["hard_filters_passed"] is True
        assert "python" in top_job["skill_gap"]["matched_skills"]
        assert "fastapi" in top_job["skill_gap"]["matched_skills"]

        # 7. Fetch Single Job Detail
        detail_resp = await client.get(f"/api/jobs/{top_job['job_id']}", headers=headers)
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["job_id"] == top_job["job_id"]
        assert detail_data["match_score"] == top_job["match_score"]

    app.dependency_overrides.clear()
