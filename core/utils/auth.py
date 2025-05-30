from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from db.session import SessionLocal
from db.models.user import User
from config import settings
import os

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Неверный токен")
    except JWTError:
        raise HTTPException(status_code=403, detail="Неверный токен")

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
