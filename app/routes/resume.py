# routes/resume.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pika
import json
import base64
import os

from app.services.crud import resume as crud
from app.schemas import resume as schemas
from app.database.database import get_db
# from app.services.salary_predictor import salary_predictor  # Removed if not used here

router = APIRouter()

def send_to_queue(resume_id: int, file_content: bytes):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
    )
    channel = connection.channel()

    channel.queue_declare(queue='resume_queue', durable=True)

    message = {
        'resume_id': resume_id,
        'file_content': base64.b64encode(file_content).decode('utf-8')
    }

    channel.basic_publish(
        exchange='',
        routing_key='resume_queue',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )

    connection.close()

@router.post("/resumes/upload", response_model=schemas.Resume)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()

    # Create a new Resume entry with minimal info
    resume = schemas.ResumeCreate(
        title="Pending",
        experience=0.0,
        key_skills="Pending",
        location="Pending",
        job_type="Pending",
        seniority_level="Pending",
        is_remote=0,
        predicted_salary=0.0
    )
    db_resume = crud.create_resume(db=db, resume=resume)

    # Send task to RabbitMQ
    send_to_queue(db_resume.id, content)

    return db_resume

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
