#main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.resume import Base
from app.database.database import engine
from app.routes import resume as resume_route

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(resume_route.router, prefix="/api/v1", tags=["resumes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Analyzer API"}
