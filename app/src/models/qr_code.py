from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
import time
from app.src.database import Base

class QRCode(Base):
    __tablename__ = "qr_codes"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    color = Column(String, nullable=False)
    size = Column(Integer, nullable=False)

    created_at = Column(BigInteger, default=lambda: int(time.time() * 1000))
    updated_at = Column(
        BigInteger,
        default=lambda: int(time.time() * 1000),
        onupdate=lambda: int(time.time() * 1000)
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
