from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, LoginIn
from app.services.user_service import create_user, authenticate_user
from app.auth import require_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
@router.post("/signup")
async def signup(payload: UserSchema, db: Session = Depends(get_db)):
    return await create_user(db, payload)
@router.post("/login")
async def login(payload: LoginIn, db: Session = Depends(get_db)):
    return await authenticate_user(db, payload)

@router.get("/me")
def me(user: User = Depends(require_user)):
    return {"id": str(user.id), "email": user.email, "role": user.role}