from pydantic import BaseModel, EmailStr
from app.schemas.project import ProjectOut


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    project: ProjectOut | None = None

    class Config:
        from_attributes = True
