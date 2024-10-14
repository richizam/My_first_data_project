# Base stage
FROM python:3.9-slim as base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Test stage
FROM base as test

RUN pip install pytest

CMD ["pytest", "-v"]

# Production stage
FROM base as prod

COPY init_db.py .
CMD ["sh", "-c", "python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]