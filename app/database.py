from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

from app.models import User,URL

def create_tables():
    Base.metadata.create_all(bind=engine)