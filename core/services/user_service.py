from sqlalchemy.orm import Session
from db.crud.user import create_user, get_user_by_username
from db.schemas.user import UserCreate
from utils.security import verify_password, create_access_token
from clients.atlassian_client import create_jira_confluence_user
from clients.gitlab_client import create_user as create_gitlab_user
from clients.sonar_client import create_user as create_sonar_user
from clients.dtrack_client import create_user as create_dtrack_user
import requests

def register_user(db: Session, user: UserCreate):
    atlassian = create_jira_confluence_user(user.username, user.email, user.full_name, user.password)
    gitlab = create_gitlab_user(user.username, user.email, user.full_name, user.password)
    sonar = create_sonar_user(user.username, user.email, user.full_name, user.password)
    # dtarck = create_dtrack_user(user.username, user.email, user.full_name, user.password)
    print(gitlab)
    return create_user(db, user, gitlab_id=gitlab["gitlab"]["id"])

def login_user(db: Session, username: str, password: str):
    db_user = get_user_by_username(db, username)
    if not db_user or not verify_password(password, db_user.hashed_password):
        return None
    token = create_access_token(data={"sub": db_user.username})
    return token
