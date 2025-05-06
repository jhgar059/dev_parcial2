from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from datetime import datetime
from utils.connection_db import Base, engine
import enum

class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserType(enum.Enum):
    REGULAR = "regular"
    PREMIUM = "premium"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    password = Column(String, nullable=False)
    status = Column(String, default=UserStatus.ACTIVE.value, nullable=False)
    user_type = Column(String, default=UserType.REGULAR.value, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def create_tables():
    """Crea todas las tablas definidas con Base"""
    Base.metadata.create_all(bind=engine)


# Ejecutar la creación de tablas al importar este módulo
create_tables()