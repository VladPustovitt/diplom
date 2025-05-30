from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.schemas.project import ProjectCreate
from services import project_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_user_project(db, project)

@router.get("/user/{user_id}")
def list_projects(user_id: int, db: Session = Depends(get_db)):
    return project_service.list_user_projects(db, user_id)
