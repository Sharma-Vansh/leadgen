"""
Unit & Integration Tests for Stage 4: Atomic Database Writer
Uses an isolated async in-memory SQLite database for deterministic test execution.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from module_2_database_and_ingestion.db.base import Base
from module_2_database_and_ingestion.db.models import Company, Job, JobSource, DedupHash
from module_2_database_and_ingestion.ingestion.stage4_writer import Stage4Writer, IngestionSummary


@pytest_asyncio.fixture
async def async_test_session():
    """Provides an isolated async in-memory SQLite session with tables created."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_atomic_write_new_job(async_test_session):
    records = [
        {
            "source_id": "SRC-0001",
            "source_name": "Naukri",
            "title": "Senior Python Developer",
            "company": "Swiggy",
            "apply_url": "https://www.naukri.com/job/swiggy-py-001",
            "location": "Bangalore, India",
            "city": "Bangalore",
            "salary_min": 1200000.0,
            "salary_max": 1800000.0,
            "salary_currency": "INR",
            "employment_type": "full_time"
        }
    ]

    summary: IngestionSummary = await Stage4Writer.write_batch(async_test_session, records)
    await async_test_session.commit()

    assert summary.inserted == 1
    assert summary.merged == 0
    assert summary.failed == 0

    # Query from database
    stmt = select(Job).where(Job.apply_url == "https://www.naukri.com/job/swiggy-py-001")
    result = await async_test_session.execute(stmt)
    saved_job = result.scalars().first()

    assert saved_job is not None
    assert saved_job.title == "Senior Python Developer"
    assert saved_job.salary_min == 1200000.0


@pytest.mark.asyncio
async def test_reingestion_merges_provenance(async_test_session):
    record1 = {
        "source_id": "SRC-0001",
        "source_name": "Naukri",
        "title": "Backend SDE-2",
        "company": "Razorpay",
        "apply_url": "https://naukri.com/job/razorpay-001",
        "city": "Bangalore"
    }
    # Ingest first time
    await Stage4Writer.write_batch(async_test_session, [record1])
    await async_test_session.commit()

    # Ingest same job from different portal (same company, title, city -> same hash)
    record2 = {
        "source_id": "SRC-0002",
        "source_name": "LinkedIn",
        "title": "Backend SDE-2",
        "company": "Razorpay",
        "apply_url": "https://linkedin.com/jobs/view/razorpay-002",
        "city": "Bangalore"
    }
    summary2: IngestionSummary = await Stage4Writer.write_batch(async_test_session, [record2])
    await async_test_session.commit()

    assert summary2.merged == 1
    assert summary2.inserted == 0

    # Verify that the alternate URL was appended to the canonical job record
    stmt = select(Job).where(Job.apply_url == "https://naukri.com/job/razorpay-001")
    result = await async_test_session.execute(stmt)
    canonical_job = result.scalars().first()

    assert "https://linkedin.com/jobs/view/razorpay-002" in canonical_job.alternate_apply_urls
