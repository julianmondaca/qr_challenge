from sqlalchemy.orm import Session
from app.src.models.qr_code import QRCode
from app.src.schemas.qr_code import QRCodeCreate, QRCodeUpdate
from uuid import UUID
from typing import List

class QRCodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, qr_data: QRCodeCreate, user_uuid: UUID) -> QRCode:
        db_qr = QRCode(
            url=qr_data.url,
            color=qr_data.color,
            size=str(qr_data.size),
            user_uuid=user_uuid
        )
        self.db.add(db_qr)
        self.db.commit()
        self.db.refresh(db_qr)
        return db_qr

    def get_by_id(self, qr_uuid: UUID) -> QRCode | None:
        return self.db.query(QRCode).filter(QRCode.uuid == qr_uuid).first()

    def get_by_user(self, user_uuid: UUID) -> List[QRCode]:
        return self.db.query(QRCode).filter(QRCode.user_uuid == user_uuid).all()

    def update(self, qr_uuid: UUID, qr_data: QRCodeUpdate) -> QRCode | None:
        db_qr = self.get_by_id(qr_uuid)
        if not db_qr:
            return None
        
        update_data = qr_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "size":
                value = str(value)
            setattr(db_qr, key, value)
        
        self.db.commit()
        self.db.refresh(db_qr)
        return db_qr

    def get_stats(self, qr_uuid: UUID) -> dict:
        # Requirement: Use native SQL for statistics
        from sqlalchemy import text
        
        # Fetch total count
        total_scans = self.db.execute(
            text("SELECT COUNT(*) FROM scans WHERE qr_uuid = :qr_uuid"),
            {"qr_uuid": qr_uuid}
        ).scalar() or 0

        # Fetch detailed logs
        scans_query = text("""
            SELECT uuid, qr_uuid, ip, country, timezone, created_at 
            FROM scans 
            WHERE qr_uuid = :qr_uuid 
            ORDER BY created_at DESC
        """)
        result = self.db.execute(scans_query, {"qr_uuid": qr_uuid})
        
        scans = []
        for row in result:
            scans.append({
                "uuid": row[0],
                "qr_uuid": row[1],
                "ip": row[2],
                "country": row[3],
                "timezone": row[4],
                "created_at": row[5]
            })

        return {
            "qr_uuid": qr_uuid,
            "total_scans": total_scans,
            "scans": scans
        }
