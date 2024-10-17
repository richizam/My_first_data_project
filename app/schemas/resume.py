# app/schemas/resume.py

from typing import Optional
from pydantic import BaseModel, Field

class ResumeBase(BaseModel):
    title: str
    experience: float
    key_skills: str
    location: str
    job_type: str
    is_remote: int

class ResumeCreate(ResumeBase):
    predicted_salary: float = Field(default=0.0)
    # seniority_level удалён из ResumeCreate

class Resume(ResumeBase):
    id: int
    predicted_salary: float
    seniority_level: Optional[str] = None  # Сделано опциональным
    status: str  # Добавлено новое поле

    class Config:
        orm_mode = True