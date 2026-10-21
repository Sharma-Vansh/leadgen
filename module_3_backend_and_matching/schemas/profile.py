"""
Student Profile Pydantic Schemas
Defines request and response structures for student academic, professional, and demographic details.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class StudentProfileUpdate(BaseModel):
    # Academics
    degree: Optional[str] = Field(None, description="e.g. B.Tech, BCA, B.Sc, MCA")
    branch: Optional[str] = Field(None, description="e.g. Computer Science, Information Technology")
    college_name: Optional[str] = None
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0, description="CGPA on scale of 10")
    passing_year: Optional[int] = Field(None, ge=2015, le=2032, description="Graduation batch year")
    tenth_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    twelfth_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)

    # Technical Skills & Links
    skills: Optional[List[str]] = Field(default_factory=list, description="List of technical/domain skills")
    certifications: Optional[List[str]] = Field(default_factory=list)
    bio: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Job Preferences
    preferred_roles: Optional[List[str]] = Field(default_factory=list)
    preferred_locations: Optional[List[str]] = Field(default_factory=list)
    open_to_remote: Optional[bool] = True
    open_to_internships: Optional[bool] = True
    open_to_full_time: Optional[bool] = True
    min_expected_salary: Optional[float] = Field(None, description="Minimum desired salary in INR")

    # Government Eligibility Demographics
    category: Optional[str] = Field("GEN", description="GEN, OBC, SC, ST, EWS")
    domicile_state: Optional[str] = None
    date_of_birth: Optional[str] = Field(None, description="YYYY-MM-DD")
    is_differently_abled: Optional[bool] = False
    disability_percentage: Optional[float] = None


class StudentProfileResponse(BaseModel):
    id: str
    user_id: str
    degree: Optional[str] = None
    branch: Optional[str] = None
    college_name: Optional[str] = None
    cgpa: Optional[float] = None
    passing_year: Optional[int] = None
    tenth_percentage: Optional[float] = None
    twelfth_percentage: Optional[float] = None

    skills: List[str] = []
    certifications: List[str] = []
    bio: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    open_to_remote: bool = True
    open_to_internships: bool = True
    open_to_full_time: bool = True
    min_expected_salary: Optional[float] = None

    category: str = "GEN"
    domicile_state: Optional[str] = None
    date_of_birth: Optional[str] = None
    is_differently_abled: bool = False
    disability_percentage: Optional[float] = None

    profile_completeness_pct: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class ProfileCompletenessResponse(BaseModel):
    completeness_pct: float
    missing_sections: List[str]
    tips: List[str]
