from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EmailTask(Base):
    __tablename__ = "email_tasks"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String)
    content = Column(String)
    recipient_email = Column(String)
    send_time = Column(DateTime)
    is_sent = Column(Boolean, default=False)