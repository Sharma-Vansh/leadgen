"""
Government Metadata Model
Specialized schema for official government exams, PSC notices, and PSU recruitment.
"""
from datetime import date, datetime
from typing import Optional, Dict, Any
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from module_2_database_and_ingestion.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class GovernmentMetadata(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "govt_metadata"

    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    notification_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    official_pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gazette_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    min_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reservation_categories: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    application_fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    exam_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    admit_card_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    syllabus_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="govt_metadata")

    def __repr__(self) -> str:
        return f"<GovernmentMetadata(job_id={self.job_id}, notification='{self.notification_number}')>"
