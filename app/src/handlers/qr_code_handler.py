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
        qr_repo = QRCodeRepository(db)
        # 1. Create the record in DB
        qr = qr_repo.create(qr_data, current_user.uuid)
        
        # 2. Prepare tracking URL
        base_url = str(request.base_url).rstrip("/")
        tracking_url = f"{base_url}/api/v1/scan/{qr.uuid}"
        
        # 3. Generate the image
        img_buffer = QRCodeService.generate_qr_image(qr, tracking_url)
        
        # 4. Return as downloadable file with metadata in headers
        filename = f"qr_{qr.uuid}.png"
        return StreamingResponse(
            img_buffer, 
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "X-QR-UUID, X-QR-URL, X-QR-Color, X-QR-Size, X-QR-Created-At", # Important for frontend access
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
        qr_repo = QRCodeRepository(db)
        return qr_repo.get_by_user(current_user.uuid)
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
        qr_repo = QRCodeRepository(db)
        qr = qr_repo.get_by_id(qr_uuid)
        if not qr or qr.user_uuid != current_user.uuid:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR Code not found")
        return qr
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
        qr_repo = QRCodeRepository(db)
        qr = qr_repo.get_by_id(qr_uuid)
        if not qr or qr.user_uuid != current_user.uuid:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR Code not found")
        
        return qr_repo.update(qr_uuid, qr_data)
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
        
        # The tracking URL is the URL that will be encoded in the QR
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
        qr_repo = QRCodeRepository(db)
        # Verify ownership
        qr = qr_repo.get_by_id(qr_uuid)
        if not qr or qr.user_uuid != current_user.uuid:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR Code not found")
        
        return qr_repo.get_stats(qr_uuid)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting QR stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching statistics"
        )
