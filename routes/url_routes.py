from flask import Blueprint, request, redirect, jsonify
from core.models import db, URL
from core.schemas import URLCreateSchema, URLResponseSchema
from utils.url_generator import generate_short_code
from marshmallow import ValidationError

url_bp = Blueprint('url', __name__)
url_create_schema = URLCreateSchema()
url_response_schema = URLResponseSchema()

@url_bp.route('/', methods=['GET'])
def home():
    return jsonify({"message": "URL Shortener API", "endpoints": {"/shorten": "POST", "/<code>": "GET"}})

@url_bp.route('/shorten', methods=['POST'])
def shorten_url():
    try:
        data = url_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    original_url = data['url']
    short_code = generate_short_code()
    
    # Ensure unique code
    while URL.query.filter_by(short_code=short_code).first():
        short_code = generate_short_code()
    
    url_obj = URL(original_url=original_url, short_code=short_code)
    db.session.add(url_obj)
    db.session.commit()
    
    response_data = url_response_schema.dump(url_obj)
    response_data['short_url'] = f"{request.host_url}{short_code}"
    
    return jsonify(response_data)

@url_bp.route('/<code>')
def redirect_url(code):
    url_obj = URL.query.filter_by(short_code=code).first()
    if url_obj:
        return redirect(url_obj.original_url)
    return jsonify({"error": "URL not found"}), 404