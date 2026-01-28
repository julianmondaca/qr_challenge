from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.src.database import Base

class QRCode(Base):
    __tablename__ = "qr_codes"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    color = Column(String, nullable=False)
    size = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        Index("ix_qr_codes_user_uuid", "user_uuid"),
        Index("ix_qr_codes_created_at", "created_at"),
    )
