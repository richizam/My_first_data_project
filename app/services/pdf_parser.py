#pdf_parser.py

import pdfplumber
import re
import io

def parse_pdf(file_content):
    all_text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
    except Exception as e:
        return f"Error processing PDF: {e}"
    return all_text

def extract_information(parsed_text):
    # Extract title
    title_match = re.search(r"Желаемая должность и зарплата\n(.*)", parsed_text)
    title = title_match.group(1) if title_match else "Unknown"

    # Extract experience
    experience_match = re.search(r"Опыт работы\s*—\s*(.*?)(?=\n|$)", parsed_text, re.IGNORECASE)
    
    if experience_match:
        experience = experience_match.group(1).strip()
        years_match = re.search(r'(\d+)\s*(год|лет|года)', experience, re.IGNORECASE)
        months_match = re.search(r'(\d+)\s*месяц', experience, re.IGNORECASE)
        
        years = int(years_match.group(1)) if years_match else 0
        months = int(months_match.group(1)) if months_match else 0
        
        experience = round(years + months / 12, 1)
    else:
        experience = 0  # Corrected indentation

    # Extract key skills
    skills_match = re.search(r"Ключевые навыки\n(.*?)\n\n", parsed_text, re.DOTALL | re.IGNORECASE)
    if skills_match:
        key_skills = skills_match.group(1).replace('\n', ', ').strip()
    else:
        skills = re.findall(r'\b[A-Za-z]+(?:\s+[A-Za-z]+)*\b', parsed_text)
        key_skills = ', '.join(set(skills))
    
    if not key_skills:
        key_skills = "Unknown"

    # Extract location
    location_match = re.search(r"Проживает:\s*(.*)", parsed_text)
    location = location_match.group(1) if location_match else "Unknown" 

    # Extract job type
    job_type_match = re.search(r"Занятость:\s*(.*?)(?=\n|$)", parsed_text, re.IGNORECASE)
    job_type = job_type_match.group(1) if job_type_match else "Unknown"

    # Extract seniority level
    def extract_seniority(title):
        if 'junior' in title.lower():
            return 'Junior'
        elif 'senior' in title.lower():
            return 'Senior'
        else:
            return 'Mid-level'
    seniority_level = extract_seniority(title)

    # Check if remote
    is_remote = 1 if 'remote' in location.lower() else 0

    return {
        'title': title,
        'experience': experience,
        'key_skills': key_skills,
        'location': location,
        'job_type': job_type,
        'seniority_level': seniority_level,
        'is_remote': is_remote
    }