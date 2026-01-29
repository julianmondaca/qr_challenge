from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    qr_uuid: UUID
    ip: str
    country: Optional[str] = None
    timezone: Optional[str] = None
    created_at: int

    @field_validator('created_at', mode='before')
    @classmethod
    def convert_datetime_to_timestamp(cls, v):
        if isinstance(v, datetime):
            return int(v.timestamp() * 1000)
        return v

class QRCodeStats(BaseModel):
    qr_uuid: UUID
    total_scans: int
    scans: List[ScanResponse]
