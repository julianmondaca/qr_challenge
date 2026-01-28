import qrcode
from io import BytesIO
from PIL import Image
from app.src.models.qr_code import QRCode

from sqlalchemy.orm import Session
from app.src.repositories.qr_code_repository import QRCodeRepository
from app.src.schemas.qr_code import QRCodeCreate, QRCodeUpdate
from uuid import UUID
from typing import List, Tuple

class QRCodeService:
    def __init__(self, db: Session):
        self.qr_repo = QRCodeRepository(db)

    @staticmethod
    def generate_qr_image(qr_model: QRCode, tracking_url: str) -> BytesIO:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add tracking URL as data
        qr.add_data(tracking_url)
        qr.make(fit=True)

        # Create image with specific color
        fill_color = qr_model.color if qr_model.color else "black"
        
        img = qr.make_image(fill_color=fill_color, back_color="white")
        
        # Resize if needed
        size_px = int(qr_model.size)
        img = img.resize((size_px, size_px), Image.Resampling.LANCZOS)
        
        # Save to buffer
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr

    def create_qr(self, qr_data: QRCodeCreate, user_uuid: UUID, base_url: str) -> Tuple[QRCode, BytesIO]:
        qr = self.qr_repo.create(qr_data, user_uuid)
        tracking_url = f"{base_url}/api/v1/scan/{qr.uuid}"
        img_buffer = self.generate_qr_image(qr, tracking_url)
        return qr, img_buffer

    def get_user_qr_codes(self, user_uuid: UUID) -> List[QRCode]:
        return self.qr_repo.get_by_user(user_uuid)

    def get_qr_detail(self, qr_uuid: UUID, user_uuid: UUID) -> QRCode:
        qr = self.qr_repo.get_by_id(qr_uuid)
        if not qr or qr.user_uuid != user_uuid:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="QR Code not found")
        return qr

    def update_qr(self, qr_uuid: UUID, user_uuid: UUID, qr_data: QRCodeUpdate) -> QRCode:
        qr = self.get_qr_detail(qr_uuid, user_uuid)
        return self.qr_repo.update(qr_uuid, qr_data)

    def get_stats(self, qr_uuid: UUID, user_uuid: UUID) -> dict:
        self.get_qr_detail(qr_uuid, user_uuid)
        return self.qr_repo.get_stats(qr_uuid)
