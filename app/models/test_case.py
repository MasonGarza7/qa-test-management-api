from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional fields that are common in test management systems
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    project = relationship("Project", back_populates="test_cases")

    results = relationship("TestResult", back_populates="test_case")

