from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VMBase(BaseModel):
    name: str

class VMCreate(VMBase):
    project_name: int

class VMRead(VMBase):
    id: int
    end_date: datetime

    class Config:
        orm_mode = True
