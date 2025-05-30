from sqlalchemy import Column, Integer, String
from db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    ssh_key = Column(String, nullable=False)
    gitlab_id = Column(Integer, nullable=False)
