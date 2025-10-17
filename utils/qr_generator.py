"""QR code generation utilities."""
import qrcode
from io import BytesIO
import base64

def generate_qr_code(url, size=10, border=4):
    """Generate QR code for URL.
    
    Args:
        url: URL to encode in QR code
        size: Size of QR code boxes
        border: Border size around QR code
        
    Returns:
        Base64 encoded PNG image of QR code
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"