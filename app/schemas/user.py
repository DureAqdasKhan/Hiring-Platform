from pydantic import BaseModel, EmailStr, Field
class User(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: str  # "hiring_manager" | "applicant"
class LoginIn(BaseModel):
    email: EmailStr
    password: str  