# worker/worker.py

import pika
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.models.resume import Resume
from app.services.pdf_parser import parse_pdf, extract_information
from app.services.salary_predictor import SalaryPredictor
from app.services.crud import resume as crud
import time

# Настройки подключения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/resume_analyzer")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "resume_tasks"

# Настройка базы данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Инициализация SalaryPredictor
try:
    salary_predictor = SalaryPredictor()
except Exception as e:
    print(f"Error initializing SalaryPredictor: {e}")
    salary_predictor = None

def determine_seniority(experience):
    if experience < 2:
        return "Junior"
    elif 2 <= experience < 5:
        return "Mid-level"
    else:
        return "Senior"

def process_resume(task_data):
    session = SessionLocal()
    try:
        extracted_info = task_data.get("extracted_info", {})
        
        # Определение уровня должности на основе опыта
        seniority_level = determine_seniority(extracted_info.get("experience", 0))
        extracted_info['seniority_level'] = seniority_level

        # Предсказание зарплаты
        if salary_predictor:
            predicted_salary = salary_predictor.predict(extracted_info)
        else:
            predicted_salary = 0.0
        extracted_info['predicted_salary'] = predicted_salary

        # Обновление записи в базе данных
        resume_id = extracted_info.get("id")
        if resume_id:
            crud.update_resume_details(session, resume_id, extracted_info)
        else:
            # Если ID не указан, создаём новую запись
            resume_create = crud.ResumeCreate(**extracted_info)
            crud.create_resume(session, resume_create, status="completed")
        
    except Exception as e:
        print(f"Ошибка при обработке резюме: {e}")
        # Можно обновить статус на "failed" или добавить логику повторной попытки
    finally:
        session.close()

def callback(ch, method, properties, body):
    print("Получена новая задача")
    try:
        task_data = json.loads(body)
        process_resume(task_data)
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
    except Exception as e:
        print(f"Общая ошибка: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    while True:
        try:
            credentials = pika.PlainCredentials('guest', 'guest')  # Убедитесь, что креденшелы совпадают с docker-compose.yml
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            print('Воркер запущен и ожидает задач. Для остановки нажмите CTRL+C')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("Не удалось подключиться к RabbitMQ. Повторная попытка через 5 секунд...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Воркер остановлен пользователем.")
            break
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()