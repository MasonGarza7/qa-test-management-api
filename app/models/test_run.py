from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)

    # Who executed the run (nullable for now so it's flexible early on)
    executed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Timestamps
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optional metadata
    environment: Mapped[str | None] = mapped_column(String(100), nullable=True)

    project = relationship("Project", back_populates="test_runs")
    executed_by = relationship("User")

    # Add reverse relationship 
    results = relationship("TestResult", back_populates="test_run")
