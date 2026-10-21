"""
User Database Model
Represents registered students and administrative accounts.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from module_2_database_and_ingestion.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from module_3_backend_and_matching.models.student_profile import StudentProfile


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="student", nullable=False)  # student, admin
    auth_provider: Mapped[str] = mapped_column(String(32), default="email", nullable=False)  # email, google
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 1-to-1 relationship with StudentProfile
    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
