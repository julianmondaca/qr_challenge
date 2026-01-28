from sqlalchemy.orm import Session
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from app.src.models.qr_code import QRCode
from app.src.models.scans import Scan
import httpx
from uuid import UUID

class ScanService:
    def __init__(self, db: Session):
        self.db = db

    async def get_geo_info(self, ip: str) -> dict:
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

    async def record_scan_and_redirect(self, qr_uuid: UUID, request: Request) -> RedirectResponse:
        # 1. Get QR code
        qr = self.db.query(QRCode).filter(QRCode.uuid == qr_uuid).first()
        if not qr:
            raise HTTPException(status_code=404, detail="QR Code not found")

        # 2. Get client info
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0]

        geo_info = await self.get_geo_info(client_ip)

        # 3. Record scan
        new_scan = Scan(
            qr_uuid=qr.uuid,
            ip=client_ip,
            country=geo_info["country"],
            timezone=geo_info["timezone"]
        )
        self.db.add(new_scan)
        self.db.commit()

        # 4. Redirect to destination URL
        target_url = qr.url
        if not (target_url.startswith("http://") or target_url.startswith("https://")):
            target_url = f"https://{target_url}"
        
        return RedirectResponse(url=target_url)
