# worker/worker.py
# worker/worker.py

import os
import sys
import pika
import json
import base64
import time
from sqlalchemy.orm import sessionmaker
from app.database.database import Base, engine
from app.models.resume import Resume
from app.services.pdf_parser import parse_pdf, extract_information
from app.services.salary_predictor import SalaryPredictor

# Ensure /app is in PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

# Initialize database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize SalaryPredictor
model_path = os.getenv("STACKING_MODEL_PATH", "stacking_model.pkl")
try:
    salary_predictor = SalaryPredictor(model_path=model_path)
except Exception as e:
    print(f"Error initializing SalaryPredictor: {e}")
    salary_predictor = None

def process_resume(ch, method, properties, body):
    print("Received a new task.")
    try:
        data = json.loads(body)
        resume_id = data['resume_id']
        file_content = base64.b64decode(data['file_content'])

        # Parse PDF
        parsed_text = parse_pdf(file_content)
        print("Parsed text:", parsed_text)

        # Extract information
        extracted_info = extract_information(parsed_text)
        print("Extracted info:", extracted_info)

        # Predict salary
        if salary_predictor is not None:
            predicted_salary = salary_predictor.predict(extracted_info)
        else:
            predicted_salary = 0.0

        extracted_info['predicted_salary'] = predicted_salary

        # Update the database
        db = SessionLocal()
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                for key, value in extracted_info.items():
                    setattr(resume, key, value)
                db.commit()
                print(f"Resume ID {resume_id} updated successfully.")
            else:
                print(f"Resume ID {resume_id} not found.")
        finally:
            db.close()

        # Acknowledge message after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing resume: {e}")
        # Do not acknowledge the message to allow reprocessing

def connect_to_rabbitmq():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    retry_delay = 5  # seconds
    max_retries = 10
    retries = 0
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
            )
            channel = connection.channel()
            channel.queue_declare(queue='resume_queue', durable=True)
            print("Connected to RabbitMQ.")
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            retries += 1
            if retries > max_retries:
                print(f"Failed to connect to RabbitMQ after {max_retries} attempts. Exiting.")
                sys.exit(1)
            print(f"Connection to RabbitMQ failed: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

def main():
    connection, channel = connect_to_rabbitmq()

    print("Waiting for messages in 'resume_queue'.")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='resume_queue', on_message_callback=process_resume)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
