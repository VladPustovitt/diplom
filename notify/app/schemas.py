from pydantic import BaseModel
from datetime import datetime

class EmailTaskCreate(BaseModel):
    subject: str
    content: str
    recipient_email: str
    send_time: datetime

class EmailTaskResponse(BaseModel):
    id: int
    subject: str
    recipient_email: str
    send_time: datetime
    is_sent: bool

    class Config:
        orm_mode = True