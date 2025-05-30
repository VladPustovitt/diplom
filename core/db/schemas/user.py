from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    ssh_key: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True
