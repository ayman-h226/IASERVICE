from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dépendance FastAPI : fournit une session DB.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
