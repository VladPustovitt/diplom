from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.schemas.vm import VMCreate
from services import vm_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_vm(vm: VMCreate, db: Session = Depends(get_db)):
    return vm_service.create_project_vm(db, vm)

@router.get("/project/{project_id}")
def list_vms(project_id: int, db: Session = Depends(get_db)):
    return vm_service.list_project_vms(db, project_id)
