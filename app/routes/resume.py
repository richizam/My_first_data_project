#routes/resume.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.services.crud import resume as crud
from app.schemas import resume as schemas
from app.database.database import get_db
from app.services.pdf_parser import parse_pdf, extract_information
from app.services.salary_predictor import salary_predictor

router = APIRouter()

@router.post("/resumes/upload", response_model=schemas.Resume)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    parsed_text = parse_pdf(content)
    print("Parsed text:", parsed_text)  # Debug print

    extracted_info = extract_information(parsed_text)
    print("Extracted info:", extracted_info)  # Debug print

    if salary_predictor is not None:
        predicted_salary = salary_predictor.predict(extracted_info)
    else:
        predicted_salary = 0.0

    extracted_info['predicted_salary'] = predicted_salary

    resume = schemas.ResumeCreate(**extracted_info)
    return crud.create_resume(db=db, resume=resume)

@router.get("/resumes/", response_model=List[schemas.Resume])
def read_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    resumes = crud.get_resumes(db, skip=skip, limit=limit)
    return resumes

@router.get("/resumes/{resume_id}", response_model=schemas.Resume)
def read_resume(resume_id: int, db: Session = Depends(get_db)):
    db_resume = crud.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume

@router.put("/resumes/{resume_id}", response_model=schemas.Resume)
def update_resume(resume_id: int, resume: schemas.ResumeCreate, db: Session = Depends(get_db)):
    db_resume = crud.update_resume(db, resume_id=resume_id, resume=resume)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume

@router.delete("/resumes/{resume_id}", response_model=schemas.Resume)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    db_resume = crud.delete_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume
