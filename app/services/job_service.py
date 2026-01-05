from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, exists, literal
from app.models.application import Application

from app.models.job import Job
from app.schemas.job import JobCreate
from app.agent import build_hiring_manager_agent


async def create_job(db: Session, job_data: JobCreate, user_id: str):
    try:
        job = Job(
            title=job_data.title,
            description=job_data.description,
            location=job_data.location,
            salary=job_data.salary,
            hiring_manager_id=user_id,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create job")


async def get_jobs_for_manager(db: Session, user_id: str):
    try:
        jobs = db.scalars(select(Job).where(Job.hiring_manager_id == user_id).order_by(Job.posted_at.desc())).all()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")


async def get_all_jobs(db: Session):
    """Get all available jobs for browsing"""
    try:
        jobs = db.scalars(select(Job).order_by(Job.posted_at.desc())).all()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")

async def list_jobs_for_applicant(db, applicant_id):
    has_applied_expr = (
        exists(
            select(1).where(
                Application.job_id == Job.id,
                Application.applicant_id == applicant_id,
            )
        )
    ).label("has_applied")

    rows = db.execute(
        select(
            Job.id,
            Job.title,
            Job.description,
            Job.location,
            Job.salary,
            Job.posted_at,
            has_applied_expr,
        ).order_by(Job.posted_at.desc())
    ).all()

    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "location": r.location,
            "salary": r.salary,
            "posted_at": r.posted_at,
            "has_applied": bool(r.has_applied),
        }
        for r in rows
    ]

async def get_jobs(command: str, user_id: str):
    try:
        print("USER ID IN GET JOBS:", user_id)
        agent = await build_hiring_manager_agent(user_id)
        print(command)
        response = agent.run(command)  # returns RunResponse
        print("RESPONSE", response)
        return {"reply": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process job search command")
