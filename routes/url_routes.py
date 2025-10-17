"""URL shortener routes and endpoints."""
from flask import Blueprint, request, redirect, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core.models import db, URL
from core.schemas import URLCreateSchema, URLResponseSchema
from utils.url_generator import generate_short_code
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

url_bp = Blueprint('url', __name__)
url_create_schema = URLCreateSchema()
url_response_schema = URLResponseSchema()

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
    
    # Check if URL already exists
    existing = URL.query.filter_by(original_url=original_url).first()
    if existing:
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
    
    try:
        url_obj = URL(original_url=original_url, short_code=short_code)
        db.session.add(url_obj)
        db.session.commit()
        
        response_data = url_response_schema.dump(url_obj)
        response_data['short_url'] = f"{request.host_url}{short_code}"
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
        404 JSON error response if code not found
    """
    url_obj = URL.query.filter_by(short_code=code).first()
    if url_obj:
        return redirect(url_obj.original_url)
    return jsonify({"error": "URL not found"}), 404