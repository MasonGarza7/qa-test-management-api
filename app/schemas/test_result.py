from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class TestResultCreate(BaseModel):
    test_run_id: int
    test_case_id: int
    status: Literal["pass", "fail", "blocked", "skipped"]
    notes: str | None = None


class TestResultOut(BaseModel):
    id: int
    test_run_id: int
    test_case_id: int
    status: Literal["pass", "fail", "blocked", "skipped"]
    notes: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
