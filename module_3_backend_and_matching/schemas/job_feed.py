"""
Job Feed and Matching Pydantic Schemas
Defines request query parameters, individual match cards, skill gap analysis reports, and feed responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SkillGapReport(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    skill_coverage_pct: float
    recommendation: Optional[str] = None


class MatchedJobCard(BaseModel):
    job_id: str
    title: str
    company_name: str
    source_name: str
    source_id: Optional[str] = None
    apply_url: str
    location: Optional[str] = None
    city: Optional[str] = None
    is_remote: bool = False
    employment_type: str = "full_time"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "INR"
    salary_raw: Optional[str] = None
    batch_eligible: Optional[List[int]] = []
    scraped_at: Optional[str] = None

    # AI Match Score & Explanation
    match_score: float = Field(..., description="Hybrid match score from 0.0 to 100.0")
    match_badge: str = Field(..., description="High Match, Good Match, Fair Match, or Low Match")
    hard_filters_passed: bool = Field(True, description="True if candidate meets all hard criteria")
    disqualification_reasons: List[str] = []
    skill_gap: SkillGapReport
    why_matched: str


class MatchedFeedResponse(BaseModel):
    total_matches: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    items: List[MatchedJobCard]
