from fastapi import FastAPI
from app.src.database import Base, engine
from app.src.models import User, QRCode, Scan
from app.src.handlers.auth_handler import router as auth_router
from app.src.handlers.qr_code_handler import router as qr_router
from app.src.handlers.scan_handler import router as scan_router

app = FastAPI(title="QR Code Management System")

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_router)
app.include_router(qr_router)
app.include_router(scan_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to QR Code Management System API"}
