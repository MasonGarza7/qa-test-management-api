from datetime import datetime
from pydantic import BaseModel


class TestRunInfo(BaseModel):
    id: int
    project_id: int
    name: str
    environment: str | None = None
    started_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class TestResultLine(BaseModel):
    id: int
    test_case_id: int
    test_case_title: str
    status: str
    notes: str | None = None
    created_at: datetime


class TestRunReportOut(BaseModel):
    run: TestRunInfo
    results: list[TestResultLine]
