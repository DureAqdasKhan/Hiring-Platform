from app.db import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship,mapped_column, Mapped
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    salary=Column(String, nullable=True)
    posted_at = Column(DateTime, default=datetime.utcnow)
    hiring_manager_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    hiring_manager = relationship("User", back_populates="posted_jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")