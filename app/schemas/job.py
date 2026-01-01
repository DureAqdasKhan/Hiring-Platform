from pydantic import BaseModel, EmailStr, Field
class JobCreate(BaseModel):
    title: str
    description: str
    location: str
    salary: str | None = None
class Command(BaseModel):
    command: str