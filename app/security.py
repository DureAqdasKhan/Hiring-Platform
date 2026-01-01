from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set in .env")

def create_access_token(user_id: str, role: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MIN)
    payload = {"sub": user_id, "role": role, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)