from sqlalchemy.orm import Session
from db.crud.project import create_project, get_projects_by_user
from db.schemas.project import ProjectCreate
from db.models.user import User
from clients.gitlab_client import create_project as create_gitlab_project

def create_user_project(db: Session, project: ProjectCreate, user: User):
    gitlab = create_gitlab_project(project.name, project.name, user)
    return create_project(db, project)

def list_user_projects(db: Session, user_id: int):
    return get_projects_by_user(db, user_id)
