from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.application import Application
from app.models.job import Job
from app.schemas.application import ApplicationCreate


def create_application(db: Session, job_id: str, applicant_user, data: ApplicationCreate, cv_file_path: str | None):
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
        cv_file_path=cv_file_path,
        status="submitted",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def list_my_applications(db: Session, applicant_user):
    return db.scalars(select(Application).where(Application.applicant_id == applicant_user.id).order_by(Application.submitted_at.desc())).all()


def list_applications_for_job(db: Session, job_id: str, hiring_manager_user):
    job = db.scalar(select(Job).where(Job.id == int(job_id)))
    if not job:
        raise ValueError("Job not found")

    # permission check: only the job's hiring manager can view
    if str(job.hiring_manager_id) != str(hiring_manager_user.id):
        raise PermissionError("Not allowed")

    return db.scalars(select(Application).where(Application.job_id == job.id).order_by(Application.submitted_at.desc())).all()
