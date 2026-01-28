from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class QRCodeBase(BaseModel):
    url: str
    color: str = Field(..., description="HEX color (e.g., #000000)")
    size: int = Field(..., description="Dimension in pixels")

class QRCodeCreate(QRCodeBase):
    pass

class QRCodeUpdate(BaseModel):
    url: Optional[str] = None
    color: Optional[str] = None
    size: Optional[int] = None

class QRCodeResponse(QRCodeBase):
    uuid: UUID
    user_uuid: UUID
    base64_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
