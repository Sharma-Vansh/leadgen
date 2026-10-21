"""
Job Feed and Opportunities Routes
Delivers AI-matched and ranked opportunities to candidates, complete with match scores,
skill-gap analysis, and eligibility verification.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from module_2_database_and_ingestion.db.models.job import Job
from module_2_database_and_ingestion.db.models.company import Company
from module_2_database_and_ingestion.db.models.job_source import JobSource
from module_2_database_and_ingestion.db.models.govt_metadata import GovernmentMetadata
from module_3_backend_and_matching.auth.dependencies import get_db, get_current_user
from module_3_backend_and_matching.models.user import User
from module_3_backend_and_matching.models.student_profile import StudentProfile
from module_3_backend_and_matching.schemas.job_feed import (
    MatchedJobCard,
    MatchedFeedResponse,
    SkillGapReport
)
from module_3_backend_and_matching.matcher.match_orchestrator import MatchOrchestrator

router = APIRouter(prefix="/jobs", tags=["Job Feed & Matching"])


@router.get("/matched-feed", response_model=MatchedFeedResponse)
async def get_matched_job_feed(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    min_score: float = Query(0.0, ge=0.0, le=100.0, description="Minimum match percentage filter"),
    only_eligible: bool = Query(True, description="Strictly return candidates passing hard rules"),
    remote_only: Optional[bool] = Query(None, description="Filter remote positions only"),
    employment_type: Optional[str] = Query(None, description="full_time, internship, gig"),
    city: Optional[str] = Query(None, description="Filter by canonical city"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns AI-scored, personalized opportunities ranked by match score percentage.
    Incorporates hard eligibility checks and skill-gap breakdowns.
    """
    # 1. Fetch Student Profile
    stmt_prof = select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    res_prof = await db.execute(stmt_prof)
    profile = res_prof.scalars().first()

    student_dict = {
        "degree": profile.degree if profile else None,
        "branch": profile.branch if profile else None,
        "cgpa": profile.cgpa if profile else None,
        "passing_year": profile.passing_year if profile else None,
        "skills": profile.skills if profile else [],
        "preferred_roles": profile.preferred_roles if profile else [],
        "preferred_locations": profile.preferred_locations if profile else [],
        "open_to_remote": profile.open_to_remote if profile else True,
        "open_to_internships": profile.open_to_internships if profile else True,
        "open_to_full_time": profile.open_to_full_time if profile else True,
        "category": profile.category if profile else "GEN",
        "date_of_birth": profile.date_of_birth if profile else None,
        "embedding": profile.embedding if profile else None,
        "bio": profile.bio if profile else None
    }

    # 2. Fetch Active Jobs with relationships
    stmt = (
        select(Job)
        .options(
            selectinload(Job.company),
            selectinload(Job.job_source),
            selectinload(Job.govt_metadata)
        )
        .where(Job.status == "active")
    )

    if remote_only is True:
        stmt = stmt.where(Job.is_remote == True)
    if employment_type:
        stmt = stmt.where(Job.employment_type == employment_type.lower())
    if city:
        stmt = stmt.where(Job.city.ilike(f"%{city}%"))

    result = await db.execute(stmt)
    active_jobs = result.scalars().all()

    # 3. Score Each Job Listing via MatchOrchestrator
    scored_items: List[MatchedJobCard] = []

    for job in active_jobs:
        job_dict = {
            "title": job.title,
            "company_name": job.company.name if job.company else "Direct Employer",
            "employment_type": job.employment_type,
            "batch_eligible": job.batch_eligible or [],
            "skills": job.skills or [],
            "is_remote": job.is_remote,
            "city": job.city,
            "description_raw": job.description_raw,
            "description_clean": job.description_clean,
            "embedding": job.embedding,
            "govt_metadata": {
                "age_min": job.govt_metadata.age_min,
                "age_max": job.govt_metadata.age_max
            } if job.govt_metadata else None
        }

        eval_res = MatchOrchestrator.match(student_dict, job_dict)

        # Apply Hard Eligibility filter if requested
        if only_eligible and not eval_res["hard_filters_passed"]:
            continue

        # Apply Minimum Score filter
        if eval_res["match_score"] < min_score:
            continue

        sg = eval_res["skill_gap"]
        card = MatchedJobCard(
            job_id=job.id,
            title=job.title,
            company_name=job.company.name if job.company else "Direct Employer",
            source_name=job.job_source.source_name if job.job_source else "LeadGen Platform",
            source_id=job.source_id,
            apply_url=job.apply_url,
            location=job.location,
            city=job.city,
            is_remote=job.is_remote,
            employment_type=job.employment_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            salary_raw=job.salary_raw,
            batch_eligible=job.batch_eligible,
            scraped_at=job.scraped_at.isoformat() if job.scraped_at else None,
            match_score=eval_res["match_score"],
            match_badge=eval_res["match_badge"],
            hard_filters_passed=eval_res["hard_filters_passed"],
            disqualification_reasons=eval_res["disqualification_reasons"],
            skill_gap=SkillGapReport(
                matched_skills=sg["matched_skills"],
                missing_skills=sg["missing_skills"],
                skill_coverage_pct=sg["skill_coverage_pct"],
                recommendation=sg["recommendation"]
            ),
            why_matched=eval_res["why_matched"]
        )
        scored_items.append(card)

    # 4. Sort by Match Score Descending
    scored_items.sort(key=lambda x: x.match_score, reverse=True)

    # 5. Pagination
    total_count = len(scored_items)
    total_pages = max(1, (total_count + limit - 1) // limit)
    offset = (page - 1) * limit
    paginated_items = scored_items[offset:offset + limit]

    return MatchedFeedResponse(
        total_matches=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        items=paginated_items
    )


@router.get("/{job_id}", response_model=MatchedJobCard)
async def get_job_detail(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full job specifications with personalized candidate match analytics."""
    stmt = (
        select(Job)
        .options(
            selectinload(Job.company),
            selectinload(Job.job_source),
            selectinload(Job.govt_metadata)
        )
        .where(Job.id == job_id)
    )
    res = await db.execute(stmt)
    job = res.scalars().first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job opportunity not found")

    # Fetch candidate profile
    stmt_prof = select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    res_prof = await db.execute(stmt_prof)
    profile = res_prof.scalars().first()

    student_dict = {
        "degree": profile.degree if profile else None,
        "branch": profile.branch if profile else None,
        "cgpa": profile.cgpa if profile else None,
        "passing_year": profile.passing_year if profile else None,
        "skills": profile.skills if profile else [],
        "preferred_roles": profile.preferred_roles if profile else [],
        "preferred_locations": profile.preferred_locations if profile else [],
        "open_to_remote": profile.open_to_remote if profile else True,
        "open_to_internships": profile.open_to_internships if profile else True,
        "open_to_full_time": profile.open_to_full_time if profile else True,
        "category": profile.category if profile else "GEN",
        "date_of_birth": profile.date_of_birth if profile else None,
        "embedding": profile.embedding if profile else None
    }

    job_dict = {
        "title": job.title,
        "company_name": job.company.name if job.company else "Direct Employer",
        "employment_type": job.employment_type,
        "batch_eligible": job.batch_eligible or [],
        "skills": job.skills or [],
        "is_remote": job.is_remote,
        "city": job.city,
        "description_raw": job.description_raw,
        "description_clean": job.description_clean,
        "embedding": job.embedding,
        "govt_metadata": {
            "age_min": job.govt_metadata.age_min,
            "age_max": job.govt_metadata.age_max
        } if job.govt_metadata else None
    }

    eval_res = MatchOrchestrator.match(student_dict, job_dict)
    sg = eval_res["skill_gap"]

    return MatchedJobCard(
        job_id=job.id,
        title=job.title,
        company_name=job.company.name if job.company else "Direct Employer",
        source_name=job.job_source.source_name if job.job_source else "LeadGen Platform",
        source_id=job.source_id,
        apply_url=job.apply_url,
        location=job.location,
        city=job.city,
        is_remote=job.is_remote,
        employment_type=job.employment_type,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        salary_raw=job.salary_raw,
        batch_eligible=job.batch_eligible,
        scraped_at=job.scraped_at.isoformat() if job.scraped_at else None,
        match_score=eval_res["match_score"],
        match_badge=eval_res["match_badge"],
        hard_filters_passed=eval_res["hard_filters_passed"],
        disqualification_reasons=eval_res["disqualification_reasons"],
        skill_gap=SkillGapReport(
            matched_skills=sg["matched_skills"],
            missing_skills=sg["missing_skills"],
            skill_coverage_pct=sg["skill_coverage_pct"],
            recommendation=sg["recommendation"]
        ),
        why_matched=eval_res["why_matched"]
    )
