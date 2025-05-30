from sqlalchemy.orm import Session
from db.models.user import User
from db.schemas.user import UserCreate
from utils.security import get_password_hash

def create_user(db: Session, user: UserCreate, gitlab_id):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
        ssh_key=user.ssh_key, 
        gitlab_id=gitlab_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
