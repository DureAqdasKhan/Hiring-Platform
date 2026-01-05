from pydantic import BaseModel, EmailStr, Field,ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class ApplicationCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=40)
    email: EmailStr
    cover_letter: Optional[str] = Field(default=None, max_length=5000)


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    job_id: int
    applicant_id: UUID
    full_name: str
    phone: Optional[str]
    email: EmailStr
    cover_letter: Optional[str]
    status: str
    submitted_at: datetime
    cv_s3_key: Optional[str] = None
    cv_filename: Optional[str] = None
    cv_mime: Optional[str] = None
    cv_size: Optional[int] = None
    job_title: Optional[str] = None
    cv_download_url: Optional[str] = None
