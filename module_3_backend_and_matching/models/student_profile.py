"""
StudentProfile Database Model
Master profile capturing academic verification, technical skillsets,
job preferences, government demographic details, and AI embedding vectors.
"""
from typing import List, Optional, Any, TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from module_2_database_and_ingestion.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from module_3_backend_and_matching.models.user import User

# Graceful pgvector import
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None


class StudentProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "student_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    # 1. Academic Credentials & Verification
    degree: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)         # e.g., 'B.Tech', 'BCA', 'MCA'
    branch: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)        # e.g., 'Computer Science'
    college_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cgpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)              # e.g., 8.4
    passing_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True) # e.g., 2025
    tenth_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    twelfth_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # 2. Technical Skills & Portfolio
    skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)    # e.g., ['Python', 'FastAPI', 'React']
    certifications: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # 3. Job Preferences & Modality
    preferred_roles: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False) # e.g. ['Backend Developer']
    preferred_locations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False) # e.g. ['Bangalore', 'Remote']
    open_to_remote: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    open_to_internships: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    open_to_full_time: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_expected_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # in annual INR

    # 4. Government & Public Sector Eligibility Demographics
    category: Mapped[str] = mapped_column(String(32), default="GEN", nullable=False) # GEN, OBC, SC, ST, EWS
    domicile_state: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # 'YYYY-MM-DD'
    is_differently_abled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disability_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # 5. Profile Completeness & AI Vector Embedding
    profile_completeness_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    if PGVECTOR_AVAILABLE and Vector is not None:
        embedding: Mapped[Optional[Any]] = mapped_column(Vector(384), nullable=True)
    else:
        embedding: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="student_profile")

    def __repr__(self) -> str:
        return f"<StudentProfile(user_id={self.user_id}, degree='{self.degree}', passing_year={self.passing_year})>"
