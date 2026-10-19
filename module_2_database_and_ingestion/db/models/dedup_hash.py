"""
DedupHash Model
High-speed SHA-256 lookup table for Level 1 instant O(1) deduplication.
"""
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from module_2_database_and_ingestion.db.base import Base


class DedupHash(Base):
    __tablename__ = "dedup_hashes"

    hash_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # SHA-256 fingerprint
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="dedup_hashes")

    def __repr__(self) -> str:
        return f"<DedupHash(hash='{self.hash_id[:12]}...', job_id={self.job_id})>"
