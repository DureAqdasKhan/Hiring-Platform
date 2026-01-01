from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.job import Job
from app.schemas.job import JobCreate
from app.agent import build_hiring_manager_agent
async def create_job(db: Session, job_data: JobCreate, user_id: str):
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
async def get_jobs_for_user(db: Session, user_id: str):
    jobs = db.scalars(select(Job).where(Job.hiring_manager_id == user_id).order_by(Job.posted_at.desc())).all()
    return jobs
async def get_jobs( command: str, user_id: str):
    print("USER ID IN GET JOBS:", user_id)
    agent = await build_hiring_manager_agent(user_id)
    print(command)
    response =  agent.run(command)  # returns RunResponse
    print("RESPONSE", response)
    return {"reply": response}
    