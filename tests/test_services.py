#test_services.py

from app.services import pdf_parser, salary_predictor
import pytest

def test_parse_pdf():
    with open("tests/sample_resume.pdf", "rb") as pdf_file:
        content = pdf_file.read()
    parsed_text = pdf_parser.parse_pdf(content)
    assert isinstance(parsed_text, str)
    assert len(parsed_text) > 0

# test_services.py

def test_extract_information():
    sample_text = """
    Желаемая должность и зарплата
    Python Developer
    Опыт работы — 3 года 6 месяцев
    Ключевые навыки: Python, Django, FastAPI, SQL
    Проживает: Москва
    Занятость: Полная занятость
    """
    result = pdf_parser.extract_information(sample_text)
    assert result["title"].strip() == "Python Developer"  # Strip leading/trailing whitespace
    assert result["experience"] == 3.5  # Ensure this matches your expectations
    assert "Python" in result["key_skills"]
    assert result["location"] == "Москва"
    assert result["job_type"] == "Полная занятость"


@pytest.mark.skipif(salary_predictor.salary_predictor is None, reason="Salary predictor not available")
def test_salary_prediction():
    sample_data = {
        "title": "Python Developer",
        "experience": 3.5,
        "key_skills": "Python, Django, FastAPI, SQL",
        "location": "Москва",
        "job_type": "Полная занятость",
        "seniority_level": "Mid-level",
        "is_remote": 0
    }
    predicted_salary = salary_predictor.salary_predictor.predict(sample_data)
    assert isinstance(predicted_salary, float)
    assert predicted_salary > 0
