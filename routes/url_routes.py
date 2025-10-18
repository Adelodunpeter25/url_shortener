"""URL shortener routes and endpoints."""
from flask import Blueprint, request, redirect, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user
from core.models import db, URL, ClickAnalytics
from core.schemas import URLCreateSchema, URLResponseSchema, BulkURLCreateSchema
from utils.url_generator import generate_short_code
from utils.validators import is_url_reachable, is_malicious_url
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

url_bp = Blueprint('url', __name__)
url_create_schema = URLCreateSchema()
url_response_schema = URLResponseSchema()
bulk_create_schema = BulkURLCreateSchema()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@url_bp.route('/', methods=['GET'])
def home():
    """API information endpoint.
    
    Returns:
        JSON response with API information and available endpoints
    """
    return jsonify({"message": "URL Shortener API", "endpoints": {"/shorten": "POST", "/<code>": "GET"}})

@url_bp.route('/shorten', methods=['POST'])
@limiter.limit("10 per minute")
def shorten_url():
    """Create a shortened URL from the provided original URL.
    
    Rate limited to 10 requests per minute per IP.
    Returns existing short URL if the original URL was already shortened.
    
    Request Body:
        JSON with 'url' field containing the URL to shorten
        
    Returns:
        JSON response with short_url, original_url, code, and metadata
        
    Raises:
        400: Invalid URL or validation error
        429: Rate limit exceeded
        500: Database error or unable to generate unique code
    """
    try:
        data = url_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    original_url = data['url']
    expires_in_days = data.get('expires_in_days')
    password = data.get('password')
    
    # Security checks
    if is_malicious_url(original_url):
        return jsonify({"error": "URL appears to be malicious"}), 400
        
    if not is_url_reachable(original_url):
        return jsonify({"error": "URL is not reachable"}), 400
    
    # Check if URL already exists
    existing = URL.query.filter_by(original_url=original_url).first()
    if existing and not existing.is_expired():
        response_data = url_response_schema.dump(existing)
        response_data['short_url'] = f"{request.host_url}{existing.short_code}"
        return jsonify(response_data)
    
    # Generate unique code with retry limit
    for _ in range(10):
        short_code = generate_short_code()
        if not URL.query.filter_by(short_code=short_code).first():
            break
    else:
        return jsonify({"error": "Unable to generate unique code"}), 500
    
    # Calculate expiration
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    try:
        # Associate URL with current user if logged in
        user_id = current_user.id if current_user.is_authenticated else None
        url_obj = URL(original_url=original_url, short_code=short_code, expires_at=expires_at, password=password, user_id=user_id)
        db.session.add(url_obj)
        db.session.commit()
        
        response_data = url_response_schema.dump(url_obj)
        response_data['short_url'] = f"{request.host_url}{short_code}"
        response_data['has_password'] = bool(password)
        return jsonify(response_data)
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

@url_bp.route('/<code>')
def redirect_url(code):
    """Redirect to the original URL using the short code.
    
    Args:
        code: The short code to look up
        
    Returns:
        HTTP redirect to the original URL if found
        Password prompt if URL is password protected
        404 JSON error response if code not found
    """
    url_obj = URL.query.filter_by(short_code=code).first()
    if not url_obj:
        return jsonify({"error": "URL not found"}), 404
        
    if url_obj.is_expired():
        return jsonify({"error": "URL has expired"}), 410
    
    # Check if password protected
    if url_obj.password:
        return jsonify({
            "password_required": True,
            "message": "This URL is password protected",
            "verify_url": f"{request.host_url}verify/{code}"
        }), 401
    
    # Track analytics and redirect
    return _track_and_redirect(url_obj)

@url_bp.route('/verify/<code>', methods=['POST'])
def verify_password(code):
    """Verify password for protected URL.
    
    Args:
        code: The short code to verify
        
    Returns:
        HTTP redirect if password correct
        401 error if password incorrect
    """
    from core.schemas import PasswordValidationSchema
    password_schema = PasswordValidationSchema()
    
    try:
        data = password_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    url_obj = URL.query.filter_by(short_code=code).first()
    if not url_obj:
        return jsonify({"error": "URL not found"}), 404
        
    if url_obj.is_expired():
        return jsonify({"error": "URL has expired"}), 410
    
    if url_obj.password != data['password']:
        return jsonify({"error": "Incorrect password"}), 401
    
    # Track analytics and redirect
    return _track_and_redirect(url_obj)

def _track_and_redirect(url_obj):
    """Helper function to track analytics and redirect."""
    # Track analytics
    analytics = ClickAnalytics(
        url_id=url_obj.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        referrer=request.headers.get('Referer', '')
    )
    
    # Update click count
    url_obj.click_count += 1
    
    db.session.add(analytics)
    db.session.commit()
    
    return redirect(url_obj.original_url)