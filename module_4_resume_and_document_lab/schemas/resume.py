"""
Resume Studio Schemas
Pydantic v2 models for resume tailoring, ATS scoring, and PDF generation requests.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TailorResumeRequest(BaseModel):
    job_id: Optional[str] = Field(None, description="Database ID of target job")
    custom_job_title: Optional[str] = None
    custom_company_name: Optional[str] = None
    custom_job_skills: Optional[List[str]] = Field(default_factory=list)
    custom_job_description: Optional[str] = None


class ATSScoreReport(BaseModel):
    ats_score: float
    grade: str
    breakdown: Dict[str, float]
    tips: List[str]
    is_ats_compliant: bool


class TailoredResumeResponse(BaseModel):
    resume_data: Dict[str, Any]
    ats_score_report: ATSScoreReport
    pdf_download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
