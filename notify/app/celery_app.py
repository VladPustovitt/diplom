from celery import Celery
from config import settings
from database import SessionLocal
from models import EmailTask
import smtplib
from email.mime.text import MIMEText

celery = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery.task(bind=True, retry_backoff=True)
def send_email(self, task_id: int):
    db = SessionLocal()
    try:
        task = db.query(EmailTask).get(task_id)
        if not task or task.is_sent:
            return

        msg = MIMEText(task.content)
        msg['Subject'] = task.subject
        msg['From'] = settings.SMTP_USER
        msg['To'] = task.recipient_email

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        task.is_sent = True
        db.commit()
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()