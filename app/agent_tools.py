"""Custom tools for the AI agent to perform write operations on the database"""
from sqlalchemy import text
from app.db import SessionLocal
from typing import Optional
import uuid


def create_job_posting(
    hiring_manager_id: str,
    title: str,
    description: str,
    location: str,
    salary: Optional[str] = None
) -> str:
    """
    Create a new job posting in the database.
    
    Args:
        hiring_manager_id: UUID of the hiring manager
        title: Job title
        description: Job description
        location: Job location
        salary: Optional salary information
        
    Returns:
        String confirmation with job details
    """
    db = SessionLocal()
    try:
        query = text("""
            INSERT INTO jobs (title, description, location, salary, hiring_manager_id, posted_at)
            VALUES (:title, :description, :location, :salary, :hiring_manager_id, NOW())
            RETURNING id, title, description, location, salary, posted_at
        """)
        
        result = db.execute(query, {
            "title": title,
            "description": description,
            "location": location,
            "salary": salary,
            "hiring_manager_id": hiring_manager_id
        })
        db.commit()
        
        row = result.fetchone()
        return f"Job created successfully! ID: {row.id}, Title: {row.title}, Location: {row.location}, Salary: {row.salary or 'Not specified'}, Posted: {row.posted_at}"
    except Exception as e:
        db.rollback()
        return f"Error creating job: {str(e)}"
    finally:
        db.close()


def update_application_status(
    application_id: str,
    hiring_manager_id: str,
    new_status: str
) -> str:
    """
    Update the status of an application.
    
    Args:
        application_id: UUID of the application
        hiring_manager_id: UUID of the hiring manager (for authorization)
        new_status: New status (submitted, reviewed, shortlisted, rejected, accepted)
        
    Returns:
        String confirmation with updated details
    """
    valid_statuses = ['submitted', 'reviewed', 'shortlisted', 'rejected', 'accepted']
    if new_status not in valid_statuses:
        return f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
    
    db = SessionLocal()
    try:
        # First verify the application belongs to this hiring manager's job
        verify_query = text("""
            SELECT a.id, a.full_name, j.title 
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = :application_id AND j.hiring_manager_id = :hiring_manager_id
        """)
        
        verify_result = db.execute(verify_query, {
            "application_id": application_id,
            "hiring_manager_id": hiring_manager_id
        }).fetchone()
        
        if not verify_result:
            return "Application not found or you don't have permission to update it."
        
        # Update the status
        update_query = text("""
            UPDATE applications 
            SET status = :new_status
            WHERE id = :application_id
            RETURNING id, full_name, status
        """)
        
        result = db.execute(update_query, {
            "application_id": application_id,
            "new_status": new_status
        })
        db.commit()
        
        row = result.fetchone()
        return f"Application status updated! Applicant: {row.full_name}, New Status: {row.status}"
    except Exception as e:
        db.rollback()
        return f"Error updating application status: {str(e)}"
    finally:
        db.close()


def delete_job_posting(
    job_id: int,
    hiring_manager_id: str
) -> str:
    """
    Delete a job posting (soft delete or hard delete based on requirements).
    
    Args:
        job_id: ID of the job to delete
        hiring_manager_id: UUID of the hiring manager (for authorization)
        
    Returns:
        String confirmation
    """
    db = SessionLocal()
    try:
        # First verify the job belongs to this hiring manager
        verify_query = text("""
            SELECT id, title FROM jobs
            WHERE id = :job_id AND hiring_manager_id = :hiring_manager_id
        """)
        
        verify_result = db.execute(verify_query, {
            "job_id": job_id,
            "hiring_manager_id": hiring_manager_id
        }).fetchone()
        
        if not verify_result:
            return "Job not found or you don't have permission to delete it."
        
        job_title = verify_result.title
        
        # Delete the job (CASCADE will handle applications)
        delete_query = text("""
            DELETE FROM jobs WHERE id = :job_id
        """)
        
        db.execute(delete_query, {"job_id": job_id})
        db.commit()
        
        return f"Job '{job_title}' (ID: {job_id}) has been deleted successfully."
    except Exception as e:
        db.rollback()
        return f"Error deleting job: {str(e)}"
    finally:
        db.close()
