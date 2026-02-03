from pydantic import BaseModel


class CoverageLine(BaseModel):
    test_case_id: int
    title: str
    status: str  # pass / fail / blocked / skipped / not_run
    notes: str | None = None


class TestRunCoverageOut(BaseModel):
    run_id: int
    project_id: int
    total_cases: int
    executed_cases: int
    not_run_cases: int
    lines: list[CoverageLine]
    pass_count: int
    fail_count: int
    blocked_count: int
    skipped_count: int
    pass_rate: float | None = None

