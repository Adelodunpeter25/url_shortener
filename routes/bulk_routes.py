"""Bulk operations and additional features routes."""
from flask import Blueprint, request, jsonify
from core.models import db, URL
from core.schemas import BulkURLCreateSchema, URLResponseSchema
from utils.url_generator import generate_short_code
from utils.validators import is_url_reachable, is_malicious_url
from utils.qr_generator import generate_qr_code
from marshmallow import ValidationError
from datetime import datetime, timedelta

bulk_bp = Blueprint('bulk', __name__)
bulk_create_schema = BulkURLCreateSchema()
url_response_schema = URLResponseSchema()

@bulk_bp.route('/bulk-shorten', methods=['POST'])
def bulk_shorten_urls():
    """Create multiple shortened URLs in one request.
    
    Request Body:
        JSON with 'urls' array containing URL objects
        
    Returns:
        JSON response with array of shortened URLs and any errors
    """
    try:
        data = bulk_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    results = []
    errors = []
    
    for i, url_data in enumerate(data['urls']):
        try:
            original_url = url_data['url']
            expires_in_days = url_data.get('expires_in_days')
            password = url_data.get('password')
            
            # Security checks
            if is_malicious_url(original_url):
                errors.append(f"URL {i+1}: Appears to be malicious")
                continue
                
            if not is_url_reachable(original_url):
                errors.append(f"URL {i+1}: Not reachable")
                continue
            
            # Check existing
            existing = URL.query.filter_by(original_url=original_url).first()
            if existing and not existing.is_expired():
                response_data = url_response_schema.dump(existing)
                response_data['short_url'] = f"{request.host_url}{existing.short_code}"
                results.append(response_data)
                continue
            
            # Generate unique code
            for _ in range(10):
                short_code = generate_short_code()
                if not URL.query.filter_by(short_code=short_code).first():
                    break
            else:
                errors.append(f"URL {i+1}: Unable to generate unique code")
                continue
            
            # Calculate expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            url_obj = URL(original_url=original_url, short_code=short_code, expires_at=expires_at, password=password)
            db.session.add(url_obj)
            
            response_data = url_response_schema.dump(url_obj)
            response_data['short_url'] = f"{request.host_url}{short_code}"
            response_data['has_password'] = bool(password)
            results.append(response_data)
            
        except Exception as e:
            errors.append(f"URL {i+1}: {str(e)}")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error during bulk operation"}), 500
    
    return jsonify({
        "results": results,
        "errors": errors,
        "total_processed": len(data['urls']),
        "successful": len(results),
        "failed": len(errors)
    })

@bulk_bp.route('/qr/<code>')
def get_qr_code(code):
    """Generate QR code for a shortened URL.
    
    Args:
        code: The short code to generate QR for
        
    Returns:
        JSON response with base64 encoded QR code image
    """
    url_obj = URL.query.filter_by(short_code=code).first()
    if not url_obj:
        return jsonify({"error": "URL not found"}), 404
        
    if url_obj.is_expired():
        return jsonify({"error": "URL has expired"}), 410
    
    short_url = f"{request.host_url}{code}"
    qr_code = generate_qr_code(short_url)
    
    return jsonify({
        "qr_code": qr_code,
        "short_url": short_url,
        "original_url": url_obj.original_url
    })

@bulk_bp.route('/analytics/<code>')
def get_analytics(code):
    """Get click analytics for a shortened URL.
    
    Args:
        code: The short code to get analytics for
        
    Returns:
        JSON response with click analytics data
    """
    url_obj = URL.query.filter_by(short_code=code).first()
    if not url_obj:
        return jsonify({"error": "URL not found"}), 404
    
    return jsonify({
        "short_code": code,
        "original_url": url_obj.original_url,
        "click_count": url_obj.click_count,
        "created_at": url_obj.created_at.isoformat(),
        "expires_at": url_obj.expires_at.isoformat() if url_obj.expires_at else None,
        "is_expired": url_obj.is_expired(),
        "recent_clicks": len([c for c in url_obj.clicks if (datetime.utcnow() - c.clicked_at).days < 7])
    })