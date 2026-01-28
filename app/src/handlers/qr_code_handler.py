from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.src.database import get_db
from app.src.repositories.qr_code_repository import QRCodeRepository
from app.src.services.qr_code_service import QRCodeService
from app.src.services.auth_service import get_current_user
from app.src.schemas.qr_code import QRCodeCreate, QRCodeUpdate, QRCodeResponse
from app.src.schemas.stats import QRCodeStats
from app.src.models.users import User
from typing import List
from uuid import UUID
import base64

router = APIRouter(prefix="/api/v1/qr-codes", tags=["qr-codes"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_qr_code(
    qr_data: QRCodeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = QRCodeService(db)
        base_url = str(request.base_url).rstrip("/")
        qr, img_buffer = service.create_qr(qr_data, current_user.uuid, base_url)
        
        filename = f"qr_{qr.uuid}.png"
        return StreamingResponse(
            img_buffer, 
            media_type="image/png",
            status_code=status.HTTP_201_CREATED,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "X-QR-UUID, X-QR-URL, X-QR-Color, X-QR-Size, X-QR-Created-At",
                "X-QR-UUID": str(qr.uuid),
                "X-QR-URL": qr.url,
                "X-QR-Color": qr.color,
                "X-QR-Size": str(qr.size),
                "X-QR-Created-At": qr.created_at.isoformat()
            }
        )
    except Exception as e:
        print(f"Error creating QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while creating the QR code"
        )

@router.get("/", response_model=List[QRCodeResponse])
def list_qr_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = QRCodeService(db)
        return service.get_user_qr_codes(current_user.uuid)
    except Exception as e:
        print(f"Error listing QR codes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching QR codes"
        )

@router.get("/{qr_uuid}", response_model=QRCodeResponse)
def get_qr_code(
    qr_uuid: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = QRCodeService(db)
        return service.get_qr_detail(qr_uuid, current_user.uuid)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching the QR code"
        )

@router.patch("/{qr_uuid}", response_model=QRCodeResponse)
def update_qr_code(
    qr_uuid: UUID,
    qr_data: QRCodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = QRCodeService(db)
        return service.update_qr(qr_uuid, current_user.uuid, qr_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while updating the QR code"
        )

@router.get("/{qr_uuid}/image")
def get_qr_image(
    qr_uuid: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        qr_repo = QRCodeRepository(db)
        qr = qr_repo.get_by_id(qr_uuid)
        if not qr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR Code not found")
        
        base_url = str(request.base_url).rstrip("/")
        tracking_url = f"{base_url}/api/v1/scan/{qr.uuid}"
        
        img_buffer = QRCodeService.generate_qr_image(qr, tracking_url)
        return StreamingResponse(img_buffer, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating QR image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while generating the QR image"
        )

@router.get("/{qr_uuid}/stats", response_model=QRCodeStats)
def get_qr_stats(
    qr_uuid: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = QRCodeService(db)
        return service.get_stats(qr_uuid, current_user.uuid)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting QR stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching statistics"
        )
