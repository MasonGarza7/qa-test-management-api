from datetime import datetime
from pydantic import BaseModel


class TestRunCreate(BaseModel):
    project_id: int
    name: str
    executed_by_user_id: int | None = None
    environment: str | None = None


class TestRunOut(BaseModel):
    id: int
    project_id: int
    name: str
    executed_by_user_id: int | None = None
    environment: str | None = None
    started_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
