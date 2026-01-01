from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ApplicationCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=40)
    email: EmailStr
    cover_letter: Optional[str] = Field(default=None, max_length=5000)


class ApplicationOut(BaseModel):
    id: UUID
    job_id: int
    applicant_id: UUID
    full_name: str
    phone: Optional[str]
    email: EmailStr
    cover_letter: Optional[str]
    cv_file_path: Optional[str]
    status: str
    submitted_at: datetime

class Config:
    from_attributes = True  # pydantic v2
