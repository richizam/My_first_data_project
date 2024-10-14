#schemas/resume.py
from pydantic import BaseModel, Field
from typing import Optional

class ResumeBase(BaseModel):
    title: str
    experience: float
    key_skills: str
    location: str
    job_type: str
    seniority_level: str
    is_remote: int

class ResumeCreate(ResumeBase):
    predicted_salary: Optional[float] = Field(default=None)

class Resume(ResumeBase):
    id: int
    predicted_salary: Optional[float] = None

    class Config:
        from_attributes = True