"""
Student Profile Routes
Endpoints for managing the master candidate profile, academic credentials,
technical skillsets, and calculating profile completeness score.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from module_3_backend_and_matching.auth.dependencies import get_db, get_current_user
from module_3_backend_and_matching.models.user import User
from module_3_backend_and_matching.models.student_profile import StudentProfile
from module_3_backend_and_matching.schemas.profile import (
    StudentProfileUpdate,
    StudentProfileResponse,
    ProfileCompletenessResponse
)
from module_3_backend_and_matching.matcher.embedder import generate_embedding
from module_3_backend_and_matching.matcher.semantic_scorer import SemanticScorer

router = APIRouter(prefix="/student/profile", tags=["Student Profile"])


def calculate_completeness(profile: StudentProfile) -> float:
    """Computes completion percentage (0.0% to 100.0%) across key sections."""
    score = 0.0

    # Section 1: Academics (30%)
    if profile.degree:
        score += 10.0
    if profile.branch:
        score += 10.0
    if profile.passing_year:
        score += 5.0
    if profile.cgpa:
        score += 5.0

    # Section 2: Technical Skills & Bio (35%)
    skills_cnt = len(profile.skills or [])
    if skills_cnt >= 5:
        score += 25.0
    elif skills_cnt >= 2:
        score += 15.0
    elif skills_cnt >= 1:
        score += 5.0

    if profile.bio and len(profile.bio.strip()) >= 30:
        score += 10.0

    # Section 3: Job Preferences (20%)
    if profile.preferred_roles:
        score += 10.0
    if profile.preferred_locations or profile.open_to_remote:
        score += 10.0

    # Section 4: Links & Demographics (15%)
    if profile.github_url or profile.linkedin_url or profile.portfolio_url:
        score += 10.0
    if profile.date_of_birth or profile.domicile_state:
        score += 5.0

    return min(100.0, round(score, 1))


@router.get("", response_model=StudentProfileResponse)
async def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the master verified student profile of the current user."""
    stmt = select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalars().first()

    if not profile:
        # Create empty profile if not yet created
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return profile


@router.put("", response_model=StudentProfileResponse)
async def update_student_profile(
    payload: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates candidate credentials and re-indexes the AI semantic vector embedding."""
    stmt = select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalars().first()

    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    update_dict = payload.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(profile, field, value)

    # Recalculate Profile Completeness Score
    profile.profile_completeness_pct = calculate_completeness(profile)

    # Re-index AI Semantic Vector Embedding
    profile_dict = {
        "degree": profile.degree,
        "branch": profile.branch,
        "skills": profile.skills,
        "preferred_roles": profile.preferred_roles,
        "bio": profile.bio
    }
    profile_text = SemanticScorer.build_student_profile_text(profile_dict)
    profile.embedding = generate_embedding(profile_text)

    await db.commit()
    await db.refresh(profile)

    return profile


@router.get("/completeness", response_model=ProfileCompletenessResponse)
async def get_profile_completeness_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns missing sections and optimization tips to improve AI job match rates."""
    stmt = select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalars().first()

    if not profile:
        return ProfileCompletenessResponse(
            completeness_pct=0.0,
            missing_sections=["Academics", "Skills", "Preferences", "Links"],
            tips=["Complete your basic academic and skill details to unlock personalized job feeds."]
        )

    missing = []
    tips = []

    if not profile.degree or not profile.branch or not profile.passing_year:
        missing.append("Academic Details (Degree, Branch, Passing Year)")
        tips.append("Add your graduation year to match with active campus hiring drives.")

    if not profile.skills or len(profile.skills) < 3:
        missing.append("Technical Skills (minimum 3 required)")
        tips.append("Add 3+ technical skills (e.g. Python, React, SQL) to improve match accuracy by 40%.")

    if not profile.preferred_roles:
        missing.append("Preferred Roles")
        tips.append("Specify roles like 'Backend Developer' or 'Data Analyst' for targeted suggestions.")

    if not (profile.github_url or profile.linkedin_url):
        missing.append("Professional Links")
        tips.append("Add GitHub or LinkedIn links for ATS verification.")

    pct = calculate_completeness(profile)

    return ProfileCompletenessResponse(
        completeness_pct=pct,
        missing_sections=missing,
        tips=tips
    )
