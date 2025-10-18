"""Authentication utilities for API keys."""
import secrets
from functools import wraps
from flask import request, jsonify, g
from flask_login import current_user
from core.models import APIKey
from datetime import datetime

def generate_api_key():
    """Generate a secure API key.
    
    Returns:
        64-character hexadecimal API key
    """
    return secrets.token_hex(32)

def api_key_required(f):
    """Decorator to require API key authentication.
    
    Checks for API key in Authorization header or api_key parameter.
    Sets g.current_user to the authenticated user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = None
        
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.split(' ')[1]
        
        # Check query parameter
        if not api_key:
            api_key = request.args.get('api_key')
        
        # Check JSON body
        if not api_key and request.is_json:
            api_key = request.get_json().get('api_key')
        
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        # Validate API key
        key_obj = APIKey.query.filter_by(key=api_key, is_active=True).first()
        if not key_obj:
            return jsonify({"error": "Invalid API key"}), 401
        
        # Update last used timestamp
        key_obj.last_used = datetime.utcnow()
        from core.models import db
        db.session.commit()
        
        # Set current user in context
        g.current_user = key_obj.user
        g.api_key = key_obj
        
        return f(*args, **kwargs)
    return decorated_function

def api_key_or_login_required(f):
    """Decorator that accepts either API key or login session.
    
    Prioritizes API key authentication over session authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try API key first
        api_key = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.split(' ')[1]
        
        if not api_key:
            api_key = request.args.get('api_key')
        
        if not api_key and request.is_json:
            api_key = request.get_json().get('api_key')
        
        if api_key:
            # Validate API key
            key_obj = APIKey.query.filter_by(key=api_key, is_active=True).first()
            if key_obj:
                key_obj.last_used = datetime.utcnow()
                from core.models import db
                db.session.commit()
                g.current_user = key_obj.user
                g.api_key = key_obj
                return f(*args, **kwargs)
            else:
                return jsonify({"error": "Invalid API key"}), 401
        
        # Fall back to session authentication
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        g.current_user = current_user
        g.api_key = None
        return f(*args, **kwargs)
    
    return decorated_function