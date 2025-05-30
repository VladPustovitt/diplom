from pydantic import BaseModel
from typing import Optional

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    user_id: int

class ProjectRead(ProjectBase):
    id: int
    status: str

    class Config:
        orm_mode = True
