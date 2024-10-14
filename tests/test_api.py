#test_api.py

from fastapi.testclient import TestClient
from app.database.database import Base, engine, get_db
import pytest

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Resume Analyzer API"}

def test_create_resume(client):
    response = client.post(
        "/api/v1/resumes/",
        json={
            "title": "Software Developer",
            "experience": 3.5,
            "key_skills": "Python, FastAPI, SQL",
            "location": "New York",
            "job_type": "Full-time",
            "seniority_level": "Mid-level",
            "is_remote": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Software Developer"
    assert "id" in data

def test_read_resumes(client):
    response = client.get("/api/v1/resumes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
