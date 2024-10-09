from fastapi import FastAPI
from app import models
from app.database import engine
from app.api.endpoints import resume

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Analyzer API")

app.include_router(resume.router, prefix="/api/v1", tags=["resumes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Analyzer API"}