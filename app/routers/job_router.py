from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.job import JobCreate, Command
from app.schemas.application import ApplicationOut
from app.services.job_service import create_job, get_jobs, get_jobs_for_user
from app.services.application_service import list_applications_for_job
from app.auth import require_user

router = APIRouter(prefix="/job", tags=["Job"])

@router.post("/post_job", status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(job_data: JobCreate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role != "hiring_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hiring managers can create jobs")
    return await create_job(db, job_data, user.id)
@router.get("/all_jobs")
async def list_all_jobs(db: Session = Depends(get_db), user: User = Depends(require_user)):
    jobs = await get_jobs_for_user(db,user.id)
    return jobs
@router.post("/my_jobs")
async def get_my_jobs(command: Command, user: User = Depends(require_user)):
    if user.role != "hiring_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hiring managers can view their jobs")
    jobs = await get_jobs(command.command, user.id)
    return jobs


@router.get("/{job_id}/applicants", response_model=list[ApplicationOut])
def get_job_applicants(job_id: str, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role != "hiring_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hiring managers can view job applicants")
    
    try:
        return list_applications_for_job(db, job_id, user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))