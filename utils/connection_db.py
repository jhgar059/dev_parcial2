from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Añadir directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database connection configuration
# Configuración especial para Clever Cloud
if os.environ.get("POSTGRESQL_ADDON_HOST"):
    # Estamos en Clever Cloud, usar PostgreSQL
    DATABASE_URL = f"postgresql://{os.environ.get('POSTGRESQL_ADDON_USER')}:{os.environ.get('POSTGRESQL_ADDON_PASSWORD')}@{os.environ.get('POSTGRESQL_ADDON_HOST')}:{os.environ.get('POSTGRESQL_ADDON_PORT')}/{os.environ.get('POSTGRESQL_ADDON_DB')}"
else:
    # Entorno de desarrollo, usar SQLite
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./sql_app.db")

# Handle PostgreSQL URL format for Clever Cloud
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()