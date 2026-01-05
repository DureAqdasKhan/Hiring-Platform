from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import engine, Base, get_db
import app.models  # IMPORTANT: registers all models


from app.routers.application_router import router as applications_router
from app.routers.job_router import router as job_router
from app.routers.user_router import router as user_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Recruitment System API", version="1.0.0")
# No migrations: create tables automatically
Base.metadata.create_all(bind=engine)
app.include_router(applications_router)
app.include_router(job_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Recruitment System API. Go to /docs"}

