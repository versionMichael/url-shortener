from fastapi import FastAPI

from app.database import create_tables

create_tables()

app = FastAPI()

@app.get("/")
def root():
    return {"message" : "URL Shortener API"}