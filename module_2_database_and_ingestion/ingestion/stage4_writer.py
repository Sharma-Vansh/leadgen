"""
Stage 4: Atomic Database Writer
Commits validated, normalized, and deduplicated records within ACID transactions.
Handles upserts, provenance merging, hash indexing, and structured ingestion summaries.
"""
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from module_2_database_and_ingestion.db.models import (
    Company,
    Job,
    JobSource,
    GovernmentMetadata,
    DedupHash
)
from module_2_database_and_ingestion.ingestion.stage2_normalizer import DateParser
from module_2_database_and_ingestion.ingestion.stage3_deduplicator import (
    HashDeduplicator,
    VectorDeduplicator
)

logger = logging.getLogger("Stage4Writer")


@dataclass
class IngestionSummary:
    total_received: int = 0
    inserted: int = 0
    merged: int = 0
    updated: int = 0
    rejected: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)


class Stage4Writer:
    """Writes normalized jobs transactionally into PostgreSQL with deduplication and provenance merging."""

    @classmethod
    async def get_or_create_company(cls, session: AsyncSession, company_name: str) -> Company:
        """Finds or creates a company entry by normalized name."""
        stmt = select(Company).where(Company.name == company_name)
        result = await session.execute(stmt)
        company = result.scalars().first()

        if not company:
            company = Company(
                id=str(uuid.uuid4()),
                name=company_name
            )
            session.add(company)
            await session.flush()

        return company

    @classmethod
    async def get_or_create_source(
        cls,
        session: AsyncSession,
        source_id: str,
        source_name: str,
        archetype: str = "A"
    ) -> JobSource:
        """Finds or creates a job source record."""
        stmt = select(JobSource).where(JobSource.source_id == source_id)
        result = await session.execute(stmt)
        source = result.scalars().first()

        if not source:
            source = JobSource(
                source_id=source_id,
                source_name=source_name,
                archetype=archetype,
                last_scraped_at=datetime.now(timezone.utc),
                total_jobs_scraped=1
            )
            session.add(source)
            await session.flush()
        else:
            source.total_jobs_scraped += 1
            source.last_scraped_at = datetime.now(timezone.utc)

        return source

    @classmethod
    async def write_batch(
        cls,
        session: AsyncSession,
        normalized_records: List[Dict[str, Any]]
    ) -> IngestionSummary:
        """
        Executes atomic batch persistence for normalized listings.
        """
        summary = IngestionSummary(total_received=len(normalized_records))

        for rec in normalized_records:
            try:
                # 1. Level 1 Exact Hash Lookup
                exact_hash = HashDeduplicator.generate_for_listing(rec)
                hash_stmt = select(DedupHash).where(DedupHash.hash_id == exact_hash)
                hash_res = await session.execute(hash_stmt)
                existing_hash = hash_res.scalars().first()

                if existing_hash:
                    # Merge provenance: append new URL if not already present
                    job_stmt = select(Job).where(Job.id == existing_hash.job_id)
                    job_res = await session.execute(job_stmt)
                    existing_job = job_res.scalars().first()

                    if existing_job:
                        incoming_url = rec.get("apply_url")
                        alt_urls = list(existing_job.alternate_apply_urls or [])
                        if incoming_url and incoming_url != existing_job.apply_url and incoming_url not in alt_urls:
                            alt_urls.append(incoming_url)
                            existing_job.alternate_apply_urls = alt_urls
                            existing_job.updated_at = datetime.now(timezone.utc)
                            logger.info(f"[Stage4Writer] Merged provenance into existing Job {existing_job.id}")
                        summary.merged += 1
                        continue

                # 2. Get or create Company & Source
                company_name = rec.get("company", "Direct Hiring")
                company = await cls.get_or_create_company(session, company_name)

                source_id = rec.get("source_id", "SRC-UNKNOWN")
                source_name = rec.get("source_name", "Unknown Platform")
                archetype = rec.get("archetype", "A")
                source = await cls.get_or_create_source(session, source_id, source_name, archetype)

                # 3. Level 2 Semantic Vector Deduplication
                embedding = rec.get("embedding")
                if not embedding and rec.get("title"):
                    embed_text = f"{rec.get('title')} {company_name} {rec.get('description_clean') or ''}"
                    embedding = VectorDeduplicator.generate_embedding(embed_text)

                if embedding:
                    is_dup, dup_job_id, sim = await VectorDeduplicator.find_semantic_duplicate(
                        session=session,
                        company_id=company.id,
                        embedding=embedding
                    )
                    if is_dup and dup_job_id:
                        dup_stmt = select(Job).where(Job.id == dup_job_id)
                        dup_res = await session.execute(dup_stmt)
                        matched_job = dup_res.scalars().first()
                        if matched_job:
                            alt_urls = list(matched_job.alternate_apply_urls or [])
                            incoming_url = rec.get("apply_url")
                            if incoming_url and incoming_url != matched_job.apply_url and incoming_url not in alt_urls:
                                alt_urls.append(incoming_url)
                                matched_job.alternate_apply_urls = alt_urls
                                matched_job.updated_at = datetime.now(timezone.utc)
                            summary.merged += 1
                            continue

                # 4. Check if apply_url already exists
                apply_url = rec["apply_url"]
                url_stmt = select(Job).where(Job.apply_url == apply_url)
                url_res = await session.execute(url_stmt)
                existing_url_job = url_res.scalars().first()

                if existing_url_job:
                    # Update fields if needed
                    existing_url_job.title = rec["title"]
                    existing_url_job.salary_min = rec.get("salary_min")
                    existing_url_job.salary_max = rec.get("salary_max")
                    existing_url_job.updated_at = datetime.now(timezone.utc)
                    summary.updated += 1
                    continue

                # 5. Insert New Job Record
                new_job_id = str(uuid.uuid4())
                new_job = Job(
                    id=new_job_id,
                    company_id=company.id,
                    source_id=source.source_id,
                    title=rec["title"],
                    description_raw=rec.get("description_raw"),
                    description_clean=rec.get("description_clean"),
                    location=rec.get("location"),
                    city=rec.get("city"),
                    country=rec.get("country", "India"),
                    is_remote=rec.get("is_remote", False),
                    employment_type=rec.get("employment_type", "full_time"),
                    salary_raw=rec.get("salary_raw"),
                    salary_min=rec.get("salary_min"),
                    salary_max=rec.get("salary_max"),
                    salary_currency=rec.get("salary_currency", "INR"),
                    apply_url=apply_url,
                    alternate_apply_urls=rec.get("alternate_apply_urls", []),
                    batch_eligible=rec.get("batch_eligible", []),
                    skills=rec.get("skills", []),
                    posted_date=rec.get("posted_date") if isinstance(rec.get("posted_date"), datetime) else (
                        DateParser.parse(rec.get("posted_date")) if rec.get("posted_date") else None
                    ),
                    deadline=rec.get("deadline") if isinstance(rec.get("deadline"), datetime) else (
                        DateParser.parse(rec.get("deadline")) if rec.get("deadline") else None
                    ),
                    scraped_at=rec.get("scraped_at") if isinstance(rec.get("scraped_at"), datetime) else (
                        DateParser.parse(rec.get("scraped_at")) if rec.get("scraped_at") else datetime.now(timezone.utc)
                    ),
                    status=rec.get("status", "discovered"),
                    embedding=embedding
                )
                session.add(new_job)

                # 6. Insert Level 1 Dedup Hash
                dedup_hash_record = DedupHash(
                    hash_id=exact_hash,
                    job_id=new_job_id
                )
                session.add(dedup_hash_record)

                # 7. Insert Government Metadata if applicable
                govt_meta = rec.get("govt_metadata")
                if govt_meta and isinstance(govt_meta, dict):
                    g_record = GovernmentMetadata(
                        id=str(uuid.uuid4()),
                        job_id=new_job_id,
                        notification_number=govt_meta.get("notification_number"),
                        official_pdf_url=govt_meta.get("official_pdf_url"),
                        gazette_link=govt_meta.get("gazette_link"),
                        min_age=govt_meta.get("min_age"),
                        max_age=govt_meta.get("max_age"),
                        reservation_categories=govt_meta.get("reservation_categories"),
                        application_fee=govt_meta.get("application_fee"),
                        exam_date=govt_meta.get("exam_date"),
                        syllabus_url=govt_meta.get("syllabus_url")
                    )
                    session.add(g_record)

                summary.inserted += 1

            except Exception as e:
                logger.error(f"[Stage4Writer] Error persisting record '{rec.get('title')}': {e}")
                summary.failed += 1
                summary.errors.append(f"{rec.get('title')}: {str(e)}")

        await session.flush()
        return summary
