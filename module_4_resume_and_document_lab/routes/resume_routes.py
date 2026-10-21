"""
Resume Studio API Routes
Endpoints for AI-assisted ATS resume tailoring, readability scoring, and PDF generation.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from module_2_database_and_ingestion.db.models.job import Job
from module_2_database_and_ingestion.db.models.company import Company
from module_3_backend_and_matching.auth.dependencies import get_db, get_current_user
from module_3_backend_and_matching.models.user import User
from module_3_backend_and_matching.models.student_profile import StudentProfile
from module_4_resume_and_document_lab.resume_studio.tailor import ResumeTailor
from module_4_resume_and_document_lab.resume_studio.ats_scorer import ATSScorer
from module_4_resume_and_document_lab.resume_studio.pdf_builder import ResumePDFBuilder
from module_4_resume_and_document_lab.schemas.resume import (
    TailorResumeRequest,
    TailoredResumeResponse,
    ATSScoreReport
)

router = APIRouter(prefix="/resume", tags=["Resume Studio"])


async def resolve_target_job_and_profile(
    payload: TailorResumeRequest,
    current_user: User,
    db: AsyncSession
) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Helper to fetch and prepare candidate and job dictionaries."""
    # 1. Fetch Student Profile
    stmt_prof = select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    res_prof = await db.execute(stmt_prof)
    profile = res_prof.scalars().first()

    if not profile or not profile.skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate profile is empty. Please add your verified skills and education first."
        )

    cand_profile_dict = {
        "degree": profile.degree,
        "branch": profile.branch,
        "college_name": profile.college_name,
        "cgpa": profile.cgpa,
        "passing_year": profile.passing_year,
        "skills": profile.skills,
        "certifications": profile.certifications,
        "bio": profile.bio,
        "github_url": profile.github_url,
        "linkedin_url": profile.linkedin_url,
        "portfolio_url": profile.portfolio_url,
        "preferred_locations": profile.preferred_locations
    }

    cand_user_dict = {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email
    }

    # 2. Resolve Target Job
    if payload.job_id:
        stmt_job = (
            select(Job)
            .options(selectinload(Job.company))
            .where(Job.id == payload.job_id)
        )
        res_job = await db.execute(stmt_job)
        job = res_job.scalars().first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target job opening not found")

        job_dict = {
            "title": job.title,
            "company_name": job.company.name if job.company else "Direct Employer",
            "skills": job.skills or [],
            "description_raw": job.description_raw,
            "description_clean": job.description_clean
        }
    else:
        job_dict = {
            "title": payload.custom_job_title or "Software Developer",
            "company_name": payload.custom_company_name or "Target Employer",
            "skills": payload.custom_job_skills or [],
            "description_clean": payload.custom_job_description or ""
        }

    return cand_profile_dict, cand_user_dict, job_dict


@router.post("/tailor", response_model=TailoredResumeResponse)
async def tailor_resume(
    payload: TailorResumeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesizes an ATS-tailored resume strictly referencing verified candidate credentials.
    Calculates ATS score and returns structured resume specification.
    """
    cand_profile, cand_user, target_job = await resolve_target_job_and_profile(payload, current_user, db)

    tailored_data = ResumeTailor.tailor_resume(
        candidate_profile=cand_profile,
        candidate_user=cand_user,
        target_job=target_job
    )

    ats_report = ATSScorer.score_resume(tailored_data)

    return TailoredResumeResponse(
        resume_data=tailored_data,
        ats_score_report=ATSScoreReport(
            ats_score=ats_report["ats_score"],
            grade=ats_report["grade"],
            breakdown=ats_report["breakdown"],
            tips=ats_report["tips"],
            is_ats_compliant=ats_report["is_ats_compliant"]
        ),
        pdf_download_url="/api/resume/download-pdf"
    )


@router.post("/download-pdf")
async def download_tailored_pdf(
    payload: TailorResumeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates and streams a single-column ATS-compliant vector PDF file.
    """
    cand_profile, cand_user, target_job = await resolve_target_job_and_profile(payload, current_user, db)

    tailored_data = ResumeTailor.tailor_resume(
        candidate_profile=cand_profile,
        candidate_user=cand_user,
        target_job=target_job
    )

    pdf_bytes = ResumePDFBuilder.generate_pdf_bytes(tailored_data)

    filename = f"{current_user.full_name.replace(' ', '_')}_Resume.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
