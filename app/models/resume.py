# models/resume.py

from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    experience = Column(Float)
    key_skills = Column(String)
    location = Column(String)
    job_type = Column(String)
    seniority_level = Column(String)
    is_remote = Column(Integer)
    predicted_salary = Column(Float)
    status = Column(String, default="processing")  # Новое поле
