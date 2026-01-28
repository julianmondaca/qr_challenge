from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.src.database import Base

class Scan(Base):
    __tablename__ = "scans"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    qr_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("qr_codes.uuid", ondelete="CASCADE"),
        nullable=False
    )

    ip = Column(String, nullable=False)
    country = Column(String, nullable=True)
    timezone = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_scans_qr_uuid", "qr_uuid"),
        Index("ix_scans_created_at", "created_at"),
        Index("ix_scans_qr_uuid_created_at", "qr_uuid", "created_at"),
    )
