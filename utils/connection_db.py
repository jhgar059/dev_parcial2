from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Para desarrollo local
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

# Para servidor remoto (descomentar y modificar si es necesario)
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgresserver/db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Función para obtener una sesión de base de datos.
    Debe ser utilizada como una dependencia en los endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()