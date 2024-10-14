#routes/resume.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.crud import resume as resume_crud
from app.schemas import resume as resume_schema
from app.services import pdf_parser, salary_predictor
from typing import List

router = APIRouter()

@router.post("/resumes/", response_model=resume_schema.Resume)
def create_resume(resume: resume_schema.ResumeCreate, db: Session = Depends(get_db)):
    return resume_crud.create_resume(db=db, resume=resume)

@router.get("/resumes/", response_model=List[resume_schema.Resume])
def read_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    resumes = resume_crud.get_resumes(db, skip=skip, limit=limit)
    return resumes

@router.get("/resumes/{resume_id}", response_model=resume_schema.Resume)
def read_resume(resume_id: int, db: Session = Depends(get_db)):
    db_resume = resume_crud.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume

@router.put("/resumes/{resume_id}", response_model=resume_schema.Resume)
def update_resume(resume_id: int, resume: resume_schema.ResumeCreate, db: Session = Depends(get_db)):
    return resume_crud.update_resume(db=db, resume_id=resume_id, resume=resume)

@router.delete("/resumes/{resume_id}", response_model=resume_schema.Resume)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    return resume_crud.delete_resume(db=db, resume_id=resume_id)

@router.post("/resumes/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    parsed_text = pdf_parser.parse_pdf(content)
    resume_data = pdf_parser.extract_information(parsed_text)

    resume = resume_schema.ResumeCreate(**resume_data)
    db_resume = resume_crud.create_resume(db=db, resume=resume)

    if salary_predictor.salary_predictor:
        predicted_salary = salary_predictor.salary_predictor.predict(resume_data)
        db_resume.predicted_salary = predicted_salary
        db.commit()

    return resume_schema.Resume.from_orm(db_resume).dict()