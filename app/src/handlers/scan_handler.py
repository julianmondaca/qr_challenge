from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.src.database import get_db
from app.src.models.qr_code import QRCode
from app.src.models.scans import Scan
import httpx
from uuid import UUID

router = APIRouter(prefix="/api/v1", tags=["scans"])

async def get_geo_info(ip: str) -> dict:
    default_info = {"country": "Unknown", "timezone": "Unknown"}
    if ip in ["127.0.0.1", "localhost", "::1"]:
        return {"country": "Localhost", "timezone": "UTC"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country", "Unknown"),
                    "timezone": data.get("timezone", "Unknown")
                }
    except Exception:
        pass
    return default_info

@router.get("/scan/{qr_uuid}")
async def scan_qr_code(
    qr_uuid: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # 1. Get QR code
        qr = db.query(QRCode).filter(QRCode.uuid == qr_uuid).first()
        if not qr:
            print(f"Tracking error: QR with UUID {qr_uuid} not found")
            raise HTTPException(status_code=404, detail="QR Code not found")

        # 2. Get client info
        client_ip = request.client.host if request.client else "unknown"
        # Check for proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0]

        geo_info = await get_geo_info(client_ip)

        # 3. Record scan
        new_scan = Scan(
            qr_uuid=qr.uuid,
            ip=client_ip,
            country=geo_info["country"],
            timezone=geo_info["timezone"]
        )
        db.add(new_scan)
        db.commit()

        # 4. Redirect to destination URL
        target_url = qr.url
        if not (target_url.startswith("http://") or target_url.startswith("https://")):
            target_url = f"https://{target_url}"
        
        print(f"Redirecting scan {qr_uuid} from {client_ip} ({geo_info['country']}/{geo_info['timezone']}) to {target_url}")
        return RedirectResponse(url=target_url)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in scan handler: {e}")
        raise HTTPException(status_code=500, detail="Error processing the scan")
