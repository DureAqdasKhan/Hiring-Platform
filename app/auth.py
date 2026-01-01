import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Header, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models.user import User

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

def require_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(required_role: str):
    def _inner(user: User = Depends(require_user)) -> User:
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _inner
