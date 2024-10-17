# Dockerfile

FROM python:3.9

WORKDIR /app

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY worker/ ./worker/
COPY stacking_model.pkl ./

# Установка дополнительных зависимостей для обработки PDF
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Команда по умолчанию для веб-приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]