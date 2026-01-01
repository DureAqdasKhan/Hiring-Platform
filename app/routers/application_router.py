from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import require_user
from app.models.user import User
from app.schemas.application import ApplicationOut, ApplicationCreate
from app.services.application_service import (
    create_application,
    list_my_applications,
    list_applications_for_job,
)
from app.services.file_service import save_upload

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/apply/{job_id}", response_model=ApplicationOut)
def apply_to_job(
    job_id: str,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str | None = Form(None),
    cover_letter: str | None = Form(None),
    cv: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    print(full_name, email, phone, cover_letter, cv)
    if user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can apply")

    cv_path = '1234.pdf'
    # save_upload(cv) if cv else None

    payload = ApplicationCreate(
        full_name=full_name,
        email=email,
        phone=phone,
        cover_letter=cover_letter,
    )

    try:
        app = create_application(db, job_id, user, payload, cv_path)
        return app
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/my", response_model=list[ApplicationOut])
def my_applications(db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can view their applications")
    return list_my_applications(db, user)


@router.get("/job/{job_id}", response_model=list[ApplicationOut])
def applications_for_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role != "hiring_manager":
        raise HTTPException(status_code=403, detail="Only hiring managers can view job applications")

    try:
        return list_applications_for_job(db, job_id, user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
