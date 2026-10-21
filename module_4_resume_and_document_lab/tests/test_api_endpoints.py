"""
Integration Tests for Module 4 API Endpoints
Tests resume tailoring, PDF streaming, signature/photo upload processing, and compliance reporting.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from module_2_database_and_ingestion.db.base import Base
from module_3_backend_and_matching.models.user import User
from module_3_backend_and_matching.models.student_profile import StudentProfile
from module_3_backend_and_matching.auth.security import create_access_token
from module_3_backend_and_matching.main import app
from module_3_backend_and_matching.auth.dependencies import get_db
from module_4_resume_and_document_lab.tests.test_photo_processor import create_sample_portrait_photo
from module_4_resume_and_document_lab.tests.test_signature_resizer import create_sample_signature_image


@pytest_asyncio.fixture
async def test_db_session():
    """Provides an isolated database session for API tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_resume_and_document_api_endpoints(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create candidate user and verified profile
    user = User(
        id="cand-001",
        email="rahul.verma@college.edu",
        full_name="Rahul Verma",
        role="student",
        is_active=True
    )
    profile = StudentProfile(
        user_id="cand-001",
        degree="B.Tech",
        branch="Information Technology",
        passing_year=2025,
        cgpa=8.4,
        skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        preferred_roles=["Backend Developer"],
        preferred_locations=["Bangalore"]
    )
    test_db_session.add_all([user, profile])
    await test_db_session.commit()

    token = create_access_token({"sub": "cand-001", "email": "rahul.verma@college.edu", "role": "student"})
    headers = {"Authorization": f"Bearer {token}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test POST /api/resume/tailor
        tailor_payload = {
            "custom_job_title": "Junior Python Developer",
            "custom_company_name": "Razorpay",
            "custom_job_skills": ["Python", "FastAPI", "PostgreSQL"],
            "custom_job_description": "We need backend developers experienced in Python and relational DBs."
        }
        tailor_resp = await client.post("/api/resume/tailor", json=tailor_payload, headers=headers)
        assert tailor_resp.status_code == 200, tailor_resp.text
        tailor_json = tailor_resp.json()
        assert "resume_data" in tailor_json
        assert tailor_json["ats_score_report"]["ats_score"] >= 75.0
        assert tailor_json["ats_score_report"]["is_ats_compliant"] is True

        # 2. Test POST /api/resume/download-pdf
        pdf_resp = await client.post("/api/resume/download-pdf", json=tailor_payload, headers=headers)
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert pdf_resp.content.startswith(b"%PDF")

        # 3. Test POST /api/documents/process-signature
        raw_sig = create_sample_signature_image()
        files = {"file": ("signature.jpg", raw_sig, "image/jpeg")}
        sig_resp = await client.post("/api/documents/process-signature", files=files)
        assert sig_resp.status_code == 200, sig_resp.text
        sig_data = sig_resp.json()
        assert sig_data["is_compliant"] is True
        assert 10.0 <= sig_data["size_kb"] <= 20.0
        assert sig_data["width"] == 300
        assert sig_data["height"] == 100

        # 4. Test POST /api/documents/process-photo
        raw_photo = create_sample_portrait_photo()
        files_photo = {"file": ("photo.jpg", raw_photo, "image/jpeg")}
        photo_resp = await client.post("/api/documents/process-photo", files=files_photo)
        assert photo_resp.status_code == 200, photo_resp.text
        photo_data = photo_resp.json()
        assert photo_data["is_compliant"] is True
        assert 20.0 <= photo_data["size_kb"] <= 50.0
        assert photo_data["width"] == 350
        assert photo_data["height"] == 450

        # 5. Test POST /api/documents/verify-compliance
        files_check = {"file": ("photo.jpg", raw_photo, "image/jpeg")}
        data_check = {"portal_code": "SSC", "document_type": "photo"}
        check_resp = await client.post("/api/documents/verify-compliance", files=files_check, data=data_check)
        assert check_resp.status_code == 200
        check_json = check_resp.json()
        assert check_json["portal"] == "SSC"
        assert check_json["document_type"] == "photo"

    app.dependency_overrides.clear()
