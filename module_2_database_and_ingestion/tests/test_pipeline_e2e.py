"""
End-to-End Pipeline Integration Tests
Validates the entire 5-stage ingestion pipeline with Module 1 StandardJobListing payloads.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from module_1_scraping_engine.core.schema import StandardJobListing
from module_2_database_and_ingestion.db.base import Base
from module_2_database_and_ingestion.db.models import Job, DedupHash
from module_2_database_and_ingestion.ingestion.pipeline_manager import PipelineManager, PipelineExecutionReport


@pytest_asyncio.fixture
async def async_test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_module1_to_module2_pipeline_e2e(async_test_db):
    # 1. Create realistic Module 1 payloads
    job1 = StandardJobListing(
        source_id="SRC-0036",
        source_name="Remotive",
        title="Full Stack Python Engineer",
        company="GitLab",
        apply_url="https://remotive.com/job/gitlab-001",
        location="Bengaluru / Remote",
        salary_raw="15.0 - 25.0 LPA",
        employment_type="full_time"
    )

    job2 = StandardJobListing(
        source_id="SRC-0001",
        source_name="Naukri",
        title="Junior Android Intern",
        company="PhonePe",
        apply_url="https://naukri.com/job/phonepe-002",
        location="Bangalore",
        salary_raw="₹40,000 per month",
        employment_type="internship"
    )

    # Invalid record (missing title)
    job3_invalid = {
        "source_id": "SRC-0005",
        "source_name": "Shine",
        "title": "",
        "company": "TCS",
        "apply_url": "https://shine.com/job/003"
    }

    raw_batch = [job1, job2, job3_invalid]

    # 2. Run master pipeline
    report: PipelineExecutionReport = await PipelineManager.process_batch(
        session=async_test_db,
        records=raw_batch,
        correlation_id="test-e2e-001"
    )
    await async_test_db.commit()

    # 3. Assert report metrics
    assert report.total_received == 3
    assert report.validation_passed == 2
    assert report.validation_rejected == 1
    assert report.inserted == 2
    assert report.failed == 0
    assert report.duration_ms > 0

    # 4. Verify DB storage and normalization for job1 (GitLab)
    stmt1 = select(Job).where(Job.apply_url == "https://remotive.com/job/gitlab-001")
    res1 = await async_test_db.execute(stmt1)
    saved_job1 = res1.scalars().first()

    assert saved_job1 is not None
    assert saved_job1.city == "Bangalore"
    assert saved_job1.is_remote is True
    assert saved_job1.salary_min == 1500000.0
    assert saved_job1.salary_max == 2500000.0
    assert saved_job1.salary_currency == "INR"

    # 5. Verify DB storage and normalization for job2 (PhonePe)
    stmt2 = select(Job).where(Job.apply_url == "https://naukri.com/job/phonepe-002")
    res2 = await async_test_db.execute(stmt2)
    saved_job2 = res2.scalars().first()

    assert saved_job2 is not None
    assert saved_job2.employment_type == "internship"
    assert saved_job2.salary_min == 480000.0  # 40k * 12

    # 6. Verify DedupHash exists
    hash_stmt = select(DedupHash).where(DedupHash.job_id == saved_job1.id)
    hash_res = await async_test_db.execute(hash_stmt)
    assert hash_res.scalars().first() is not None
