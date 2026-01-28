from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.src.database import get_db
from app.src.models.qr_code import QRCode
from app.src.models.scans import Scan
import httpx
from uuid import UUID

from app.src.services.scan_service import ScanService
from uuid import UUID

router = APIRouter(prefix="/api/v1", tags=["scans"])

@router.get("/scan/{qr_uuid}")
async def scan_qr_code(
    qr_uuid: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        service = ScanService(db)
        return await service.record_scan_and_redirect(qr_uuid, request)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in scan handler: {e}")
        raise HTTPException(status_code=500, detail="Error processing the scan")
