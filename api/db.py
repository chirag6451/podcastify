import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "chiragahmedabadi")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "indapoint")
POSTGRES_DB = os.getenv("POSTGRES_DB", "podcraftai")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create engine with optimized pool settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,  # Increase from default 5
    max_overflow=30,  # Increase from default 10
    pool_timeout=60,  # Increase from default 30
    pool_pre_ping=True  # Enable connection health checks
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
