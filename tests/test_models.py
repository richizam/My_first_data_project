# test_models.py

from app.models.resume import Resume

def test_create_resume(test_db):  # Using the test_db fixture
    resume = Resume(
        title="Software Engineer",
        experience=5.0,
        key_skills="Python, JavaScript, SQL",
        location="San Francisco",
        job_type="Full-time",
        seniority_level="Senior",
        is_remote=0
    )
    test_db.add(resume)
    test_db.commit()
    test_db.refresh(resume)
    assert resume.id is not None
    assert resume.title == "Software Engineer"
