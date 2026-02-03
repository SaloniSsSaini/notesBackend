from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
import uuid
from database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

    is_deleted = Column(Boolean, default=False)

    created_by = Column(String, default="system")
    updated_by = Column(String, default="system")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
