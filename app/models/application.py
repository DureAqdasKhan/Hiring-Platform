from app.db import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("job_id", "applicant_id", name="uq_applicant_job"),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)  # match jobs.id type
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    cover_letter = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="submitted")
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    cv_s3_key = Column(String, nullable=True)
    cv_filename = Column(String, nullable=True)
    cv_mime = Column(String, nullable=True)
    cv_size = Column(Integer, nullable=True)

    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
