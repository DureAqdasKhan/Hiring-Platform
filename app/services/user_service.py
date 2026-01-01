from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import User as UserSchema, LoginIn
from app.security import hash_password, verify_password, create_access_token
async def create_user(db: Session, user_data: UserSchema):
    if user_data.role not in ("hiring_manager", "applicant"):
        raise HTTPException(status_code=400, detail="role must be hiring_manager or applicant")

    existing = db.scalar(select(User).where(User.email == user_data.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": str(user.id), "email": user.email, "role": user.role}


async def authenticate_user(db: Session, payload: LoginIn):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=str(user.id), role=user.role)
    return {"access_token": token, "token_type": "bearer"}