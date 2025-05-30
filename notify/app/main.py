from fastapi import FastAPI
from routes import router
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification API",
    openapi_url="/api/notification/openapi.json",
    docs_url="/api/notification/docs",
    redoc_url="/api/notification/redoc")

app.include_router(router)