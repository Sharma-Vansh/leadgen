"""
Job Model
Master table for all opportunities with salary, location, provenance, and pgvector embeddings.
"""
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from module_2_database_and_ingestion.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# Graceful pgvector import
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None


class Job(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "jobs"

    # Foreign Keys
    company_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("job_sources.source_id", ondelete="SET NULL"), nullable=True, index=True)

    # Core Listing Details
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_clean: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location & Work Modality
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(64), default="India", nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Classification & Eligibility
    employment_type: Mapped[str] = mapped_column(String(64), default="full_time", index=True)  # full_time, internship, contract, gig
    experience_min: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    experience_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    batch_eligible: Mapped[Optional[List[int]]] = mapped_column(JSON, default=list, nullable=True)
    skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Compensation (Normalized Annual INR)
    salary_raw: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    salary_currency: Mapped[str] = mapped_column(String(16), default="INR", nullable=False)

    # Application URLs & Multi-Portal Provenance
    apply_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    alternate_apply_urls: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)  # Preserves multi-portal source links

    # Dates
    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Lifecycle Status (10 States)
    status: Mapped[str] = mapped_column(
        String(32),
        default="discovered",
        index=True,
        nullable=False
    )

    # Vector Embedding (384-dimensional dense vector for semantic search)
    if PGVECTOR_AVAILABLE:
        embedding: Mapped[Optional[Any]] = mapped_column(Vector(384), nullable=True)
    else:
        embedding: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationships
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="jobs")
    job_source: Mapped[Optional["JobSource"]] = relationship("JobSource", back_populates="jobs")
    govt_metadata: Mapped[Optional["GovernmentMetadata"]] = relationship("GovernmentMetadata", back_populates="job", uselist=False, cascade="all, delete-orphan")
    dedup_hashes: Mapped[List["DedupHash"]] = relationship("DedupHash", back_populates="job", cascade="all, delete-orphan")
    payment_records: Mapped[List["PaymentRecord"]] = relationship("PaymentRecord", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', status='{self.status}')>"
