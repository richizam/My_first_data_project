from app.database.database import engine
from app.models import resume as resume_model

def init_db():
    resume_model.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()