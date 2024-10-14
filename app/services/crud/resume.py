#service/crud/resume.py
from sqlalchemy.orm import Session
from app.models import resume as models
from app.schemas import resume as schemas

def get_resume(db: Session, resume_id: int):
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()

def get_resumes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Resume).offset(skip).limit(limit).all()

def create_resume(db: Session, resume: schemas.ResumeCreate):
    db_resume = models.Resume(**resume.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def update_resume(db: Session, resume_id: int, resume: schemas.ResumeCreate):
    db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if db_resume:
        for key, value in resume.dict().items():
            setattr(db_resume, key, value)
        db.commit()
        db.refresh(db_resume)
    return db_resume

def delete_resume(db: Session, resume_id: int):
    db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume