from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.session import SessionLocal
from services import user_service
from db.schemas.user import UserCreate
from services import project_service, vm_service
from db.schemas.project import ProjectCreate
from db.schemas.vm import VMCreate
from jose import jwt
from config import settings
from db.models.project import Project
from utils.auth import get_current_user
from db.models.user import User
import os

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    token = user_service.login_user(db, username, password)
    if not token:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные учетные данные"})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("access_token", token, httponly=True)
    return response

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(request: Request, response: Response, username: str = Form(...), full_name: str = Form(...), password: str = Form(...), ssh_key: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    user_data = UserCreate(username=username, full_name=full_name, password=password, ssh_key=ssh_key, email=email)
    user_service.register_user(db, user_data)
    return RedirectResponse(url="/login", status_code=303)

def get_user_id_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("sub")

@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_id_from_cookie(request)
    if not user:
        return RedirectResponse("/login")
    db_user = user_service.get_user_by_username(db, user)
    projects = project_service.list_user_projects(db, db_user.id)
    return templates.TemplateResponse("dashboard.html", {"request": request, "projects": projects})

@router.post("/projects/create")
def create_project(request: Request, name: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_id_from_cookie(request)
    db_user = user_service.get_user_by_username(db, user)
    project = ProjectCreate(name=name, user_id=db_user.id)
    project_service.create_user_project(db, project, current_user)
    return RedirectResponse("/dashboard", status_code=303)

@router.get("/projects/{project_id}")
def project_detail(request: Request, project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter_by(id=project_id).first()
    vms = vm_service.list_project_vms(db, project_id)
    return templates.TemplateResponse("project_detail.html", {"request": request, "project": project, "vms": vms})

@router.post("/projects/{project_id}/vms/create")
def create_vm(request: Request, project_id: int, name: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter_by(id=project_id).first()
    vm = VMCreate(name=name, project_name=project.name)
    vm_service.create_project_vm(db, vm, current_user)
    return RedirectResponse(f"/projects/{project_id}", status_code=303)

@router.get("/logout")
def logout(current_user: User = Depends(get_current_user)):
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response