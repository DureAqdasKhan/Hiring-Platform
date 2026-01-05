from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.auth import require_user
from app.models.user import User
from app.models.application import Application
from app.schemas.application import ApplicationOut, ApplicationCreate
from app.services.application_service import (
    create_application,
    list_my_applications,
    list_applications_for_job,
    get_my_application_for_job,
    get_all_user_applications,
)
from app.services.file_service import save_upload
from app.s3 import presign_get_url
from app.services.email_service import send_application_confirmation

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/apply/{job_id}", response_model=ApplicationOut)
def apply_to_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str | None = Form(None),
    cover_letter: str | None = Form(None),
    cv: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    if user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can apply")

    payload = ApplicationCreate(
        full_name=full_name,
        email=email,
        phone=phone,
        cover_letter=cover_letter,
    )

    try:
        app = create_application(db, job_id, user, payload, cv)
        background_tasks.add_task(
            send_application_confirmation,
            to_email=app.email,
            applicant_name=app.full_name,
            job_title=app.job.title if hasattr(app, "job") and app.job else f"Job #{app.job_id}",
        )
        return app
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{application_id}/cv-link")
def get_cv_link(
    application_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    app = db.scalar(select(Application).where(Application.id == application_id))
    if not app or not app.cv_s3_key:
        raise HTTPException(status_code=404, detail="CV not found")

    # TODO (later): authorize hiring manager owns the job OR applicant owns application

    url = presign_get_url(app.cv_s3_key)
    return {"url": url}

@router.get("/my", response_model=list[ApplicationOut])
def my_applications(db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can view their applications")
    return list_my_applications(db, user)


@router.get("/my/{job_id}")
def my_application_for_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(require_user)):
    """Get current applicant's application for a specific job with CV download link"""
    if user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can view their applications")
    
    app = get_my_application_for_job(db, job_id, user)
    
    # Convert to dict and add CV download URL if available
    result = {
        "id": str(app.id),
        "job_id": app.job_id,
        "applicant_id": str(app.applicant_id),
        "full_name": app.full_name,
        "email": app.email,
        "phone": app.phone,
        "cover_letter": app.cover_letter,
        "status": app.status,
        "submitted_at": app.submitted_at,
        "cv_s3_key": app.cv_s3_key,
        "cv_filename": app.cv_filename,
        "cv_mime": app.cv_mime,
        "cv_size": app.cv_size,
        "cv_download_url": presign_get_url(app.cv_s3_key) if app.cv_s3_key else None
    }
    return result


@router.get("/job/{job_id}", response_model=list[ApplicationOut])
def applications_for_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(require_user)):
    """Get all applications for a specific job including CV download links and cover letters"""
    if user.role != "hiring_manager":
        raise HTTPException(status_code=403, detail="Only hiring managers can view job applications")

    try:
        applications = list_applications_for_job(db, job_id, user)
        
        # Add CV download URLs to each application
        result = []
        for app in applications:
            app.cv_download_url = presign_get_url(app.cv_s3_key) if app.cv_s3_key else None
            result.append(app)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/all", response_model=list[ApplicationOut])
def get_all_applications(db: Session = Depends(get_db), user: User = Depends(require_user)):
    """
    Get all applications for the current user:
    - Applicants: returns their submitted applications
    - Hiring Managers: returns all applications across all their posted jobs
    """
    applications = get_all_user_applications(db, user)
    
    # Add CV download URLs to each application
    result = []
    for app in applications:
        app.cv_download_url = presign_get_url(app.cv_s3_key) if app.cv_s3_key else None
        result.append(app)
    
    return result
