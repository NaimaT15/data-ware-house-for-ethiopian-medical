from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv('.env')

# Fetch database URL from the environment
DATABASE_URL = os.getenv('DB_URL')

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True)  # Added `echo=True` for debug logging
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    """
    Dependency to get a database session for FastAPI endpoints.
    Automatically closes the session after use.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise e  # Re-raise the exception
    finally:
        db.close()
