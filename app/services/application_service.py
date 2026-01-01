from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.application import Application
from app.models.job import Job
from app.schemas.application import ApplicationCreate
from fastapi import HTTPException, UploadFile
from uuid import UUID
from app.s3 import build_cv_key, upload_cv_file, presign_get_url

def create_application(
    db: Session,
    job_id: str,
    applicant_user,
    data: ApplicationCreate,
    cv: UploadFile | None,
):
    job = db.scalar(select(Job).where(Job.id == int(job_id)))
    if not job:
        raise ValueError("Job not found")

    app = Application(
        job_id=job.id,
        applicant_id=applicant_user.id,
        full_name=data.full_name,
        phone=data.phone,
        email=str(data.email),
        cover_letter=data.cover_letter,
        status="submitted",
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # upload CV + update row
    if cv:
        key = build_cv_key(str(app.id), cv.filename or "cv")
        upload_cv_file(cv, key)

        app.cv_s3_key = key
        app.cv_filename = cv.filename
        app.cv_mime = cv.content_type
        db.commit()
        db.refresh(app)

    return app

def get_application_by_id(db: Session, application_id: str) -> Application:
    try:
        app_id = UUID(application_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid application_id")

    app = db.scalar(select(Application).where(Application.id == app_id))
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


def get_application_cv_link(
    db: Session,
    application_id: str,
    user,
) -> str:
    """
    Returns a short-lived presigned URL for the application's CV.

    Authorization policy (simple):
    - applicant can access their own application CV
    - hiring manager can access CV if they own the job that application belongs to
    """
    app = get_application_by_id(db, application_id)

    if not app.cv_s3_key:
        raise HTTPException(status_code=404, detail="CV not found")

    # Applicant can access their own
    if getattr(user, "role", None) == "applicant":
        if str(app.applicant_id) != str(user.id):
            raise HTTPException(status_code=403, detail="Not allowed")
        return presign_get_url(app.cv_s3_key)

    # Hiring manager can access if they own the job
    if getattr(user, "role", None) == "hiring_manager":
        job = db.scalar(select(Job).where(Job.id == app.job_id))
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if str(job.hiring_manager_id) != str(user.id):
            raise HTTPException(status_code=403, detail="Not allowed")
        return presign_get_url(app.cv_s3_key)

    raise HTTPException(status_code=403, detail="Not allowed")

def list_my_applications(db: Session, applicant_user):
    return db.scalars(select(Application).where(Application.applicant_id == applicant_user.id).order_by(Application.submitted_at.desc())).all()


def get_my_application_for_job(db: Session, job_id: str, applicant_user):
    """Get the current applicant's application for a specific job"""
    try:
        job_id_int = int(job_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid job_id")
    
    # Check if job exists
    job = db.scalar(select(Job).where(Job.id == job_id_int))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get the applicant's application for this job
    app = db.scalar(
        select(Application).where(
            (Application.job_id == job_id_int) & 
            (Application.applicant_id == applicant_user.id)
        )
    )
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return app

def list_applications_for_job(db: Session, job_id: str, hiring_manager_user):
    job = db.scalar(select(Job).where(Job.id == int(job_id)))
    if not job:
        raise ValueError("Job not found")

    # permission check: only the job's hiring manager can view
    if str(job.hiring_manager_id) != str(hiring_manager_user.id):
        raise PermissionError("Not allowed")

    return db.scalars(select(Application).where(Application.job_id == job.id).order_by(Application.submitted_at.desc())).all()
