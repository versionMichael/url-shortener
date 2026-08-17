from fastapi import FastAPI

from app.database import Base, engine
from app.models import URL, User

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message" : "URL Shortener API"}