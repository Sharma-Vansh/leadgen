"""
Core Pydantic Schema for StandardJobListing
All scrapers normalize scraped data into this unified format.
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator


class StandardJobListing(BaseModel):
    # Identifiers
    id: Optional[str] = None
    source_id: str = Field(..., description="Unique source identifier, e.g. SRC-0036")
    source_name: str = Field(..., description="Name of the platform, e.g. Remotive")
    
    # Core Details (Mandatory)
    title: str = Field(..., min_length=2, description="Job title / role name")
    company: str = Field(..., min_length=1, description="Hiring company or department")
    apply_url: str = Field(..., description="Direct link to apply or view job")

    # Location & Work Modality
    location: Optional[str] = "Remote"
    is_remote: bool = True
    country: Optional[str] = None
    city: Optional[str] = None

    # Employment & Experience
    employment_type: Optional[str] = "full_time"  # full_time, part_time, internship, contract, gig
    experience_min: Optional[int] = 0
    experience_max: Optional[int] = None
    batch_eligible: Optional[List[int]] = None

    # Compensation
    salary_raw: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = "INR"

    # Description & Skills
    description: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

    # Dates
    posted_date: Optional[str] = None  # ISO-8601: YYYY-MM-DD
    deadline: Optional[str] = None
    scraped_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Raw Payload (audit & debugging)
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("title", "company")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return " ".join(v.split()).strip()

    @field_validator("apply_url")
    @classmethod
    def clean_url(cls, v: str) -> str:
        return v.strip()
