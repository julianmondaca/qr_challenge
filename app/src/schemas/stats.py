from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ScanResponse(BaseModel):
    uuid: UUID
    qr_uuid: UUID
    ip: str
    country: Optional[str] = None
    timezone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QRCodeStats(BaseModel):
    qr_uuid: UUID
    total_scans: int
    scans: List[ScanResponse]
