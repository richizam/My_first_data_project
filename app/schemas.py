from pydantic import BaseModel, Field

class ResumeBase(BaseModel):
    title: str
    experience: float
    key_skills: str
    location: str
    job_type: str
    seniority_level: str
    is_remote: int

class ResumeCreate(ResumeBase):
    predicted_salary: float = Field(default=0.0)

class Resume(ResumeBase):
    id: int
    predicted_salary: float

    class Config:
        from_attributes = True