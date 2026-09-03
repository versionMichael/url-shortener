from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import URL, User
from app.routers.auth import router as auth_router
from app.routers.urls import router as urls_router
from app.routers.redirect import router as redirect_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(urls_router)
app.include_router(redirect_router)


@app.get("/")
async def root():
    return {"message": "URL Shortner API"}