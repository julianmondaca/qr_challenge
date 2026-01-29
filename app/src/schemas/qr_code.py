from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator
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
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    user_uuid: UUID
    base64_image: Optional[str] = None
    created_at: int
    updated_at: int

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_timestamp(cls, v):
        if isinstance(v, datetime):
            return int(v.timestamp() * 1000)
        return v
