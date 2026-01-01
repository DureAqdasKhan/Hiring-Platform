from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=False)

    cover_letter = Column(Text, nullable=True)
    cv_file_path = Column(String, nullable=True)  # local path for now (later S3 key)

    status = Column(String, nullable=False, default="submitted")  # submitted/reviewed/shortlisted/rejected
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
