import qrcode
from io import BytesIO
from PIL import Image
from app.src.models.qr_code import QRCode

class QRCodeService:
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
        # Default color is black
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
