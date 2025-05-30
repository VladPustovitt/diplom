from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import EmailTask
from schemas import EmailTaskCreate, EmailTaskResponse
from celery_app import send_email
from datetime import datetime

router = APIRouter(prefix="/api/notification", tags=["Notification"])

@router.post("/tasks/", response_model=EmailTaskResponse)
def create_task(task: EmailTaskCreate, db: Session = Depends(get_db)):
    db_task = EmailTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    send_time = task.send_time
    send_email.apply_async(args=[db_task.id], eta=send_time)
    return db_task

@router.get("/tasks/{task_id}", response_model=EmailTaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(EmailTask).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task