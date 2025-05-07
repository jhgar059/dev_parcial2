from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from data.models import User, Task
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# User operations
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_active_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()


def get_premium_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.is_premium == True).offset(skip).limit(limit).all()


def create_user(db: Session, user_data):
    hashed_password = pwd_context.hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        is_active=user_data.is_active,
        is_premium=user_data.is_premium
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user_data.dict(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data and update_data["password"]:
            update_data["password"] = pwd_context.hash(update_data["password"])

        # Update user attributes
        for key, value in update_data.items():
            setattr(db_user, key, value)

        # Update timestamp
        db_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# Task operations
def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()


def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()


def create_task(db: Session, task_data, user_id: int):
    db_task = Task(
        **task_data.dict(),
        user_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_data):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        update_data = task_data.dict(exclude_unset=True)

        # Update task attributes
        for key, value in update_data.items():
            setattr(db_task, key, value)

        # Update timestamp
        db_task.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False