from sqlalchemy.orm import Session
from .models import SessionLocal, User

def get_user_from_db(username: str):
    db: Session = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()
