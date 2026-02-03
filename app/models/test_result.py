from sqlalchemy import DateTime, ForeignKey, String, Text, func, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


TEST_STATUS_ENUM = Enum(
    "pass",
    "fail",
    "blocked",
    "skipped",
    name="test_status",
)


class TestResult(Base):
    __tablename__ = "test_results"

    __table_args__ = (
        UniqueConstraint("test_run_id", "test_case_id", name="uq_test_results_run_case"),
    )


    id: Mapped[int] = mapped_column(primary_key=True)

    test_run_id: Mapped[int] = mapped_column(ForeignKey("test_runs.id"), nullable=False)
    test_case_id: Mapped[int] = mapped_column(ForeignKey("test_cases.id"), nullable=False)

    # pass / fail / blocked / skipped
    status: Mapped[str] = mapped_column(TEST_STATUS_ENUM, nullable=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    test_run = relationship("TestRun", back_populates="results")
    test_case = relationship("TestCase")

    test_case = relationship("TestCase", back_populates="results")
    test_run = relationship("TestRun")
    