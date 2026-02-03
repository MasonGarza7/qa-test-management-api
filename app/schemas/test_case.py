from pydantic import BaseModel


class TestCaseCreate(BaseModel):
    project_id: int
    title: str
    description: str | None = None
    priority: str = "medium"


class TestCaseOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None = None
    priority: str
    is_active: bool

    class Config:
        from_attributes = True

class TestCaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    is_active: bool | None = None
