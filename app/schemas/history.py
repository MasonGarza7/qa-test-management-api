from datetime import datetime
from pydantic import BaseModel


class TestCaseHistoryLine(BaseModel):
    run_id: int
    run_name: str
    environment: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime


class TestCaseHistoryOut(BaseModel):
    test_case_id: int
    title: str
    history: list[TestCaseHistoryLine]
