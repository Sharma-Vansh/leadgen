"""
JobSource Model
Tracks metadata, scraping difficulty, health status, and metrics for all 388 sources.
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from module_2_database_and_ingestion.db.base import Base, TimestampMixin


class JobSource(Base, TimestampMixin):
    __tablename__ = "job_sources"

    source_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g., 'SRC-0001'
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    archetype: Mapped[str] = mapped_column(String(8), nullable=False, index=True)  # A, B, C, D, E
    official_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scraping_difficulty: Mapped[Optional[str]] = mapped_column(String(32), default="Medium")
    health_status: Mapped[str] = mapped_column(String(32), default="ONLINE", index=True)  # ONLINE, DEGRADED, OFFLINE
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_jobs_scraped: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="job_source")

    def __repr__(self) -> str:
        return f"<JobSource(source_id='{self.source_id}', name='{self.source_name}', archetype='{self.archetype}')>"
