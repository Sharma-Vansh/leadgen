"""
PaymentRecord Model
Stores submission evidence, transaction reference IDs, and portal confirmation numbers.
Note: Payment records store evidence and audit logs; they do not process live payments.
The student_id is stored as an identifier without a rigid foreign key constraint to defer
to Module 3 student auth models.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from module_2_database_and_ingestion.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payment_records"

    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    transaction_ref_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    challan_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    amount_paid: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payment_status: Mapped[str] = mapped_column(String(32), default="INITIATED", index=True)  # INITIATED, CONFIRMED, FAILED
    receipt_document_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confirmation_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="payment_records")

    def __repr__(self) -> str:
        return f"<PaymentRecord(id={self.id}, job_id={self.job_id}, status='{self.payment_status}')>"
