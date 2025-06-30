from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def save_answer(db: Session, user_id: int, question: str, answer: str, feedback: str):
    db_answer = models.UserAnswer(
        user_id=user_id, question=question, answer=answer, feedback=feedback
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer
