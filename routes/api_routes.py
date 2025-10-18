"""API key management routes."""
from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user
from core.models import db, APIKey
from core.schemas import APIKeyCreateSchema, APIKeyResponseSchema
from utils.auth import generate_api_key, api_key_required
from marshmallow import ValidationError

api_bp = Blueprint('api', __name__)
api_key_create_schema = APIKeyCreateSchema()
api_key_response_schema = APIKeyResponseSchema()

@api_bp.route('/keys', methods=['POST'])
@login_required
def create_api_key():
    """Create a new API key for the current user.
    
    Request Body:
        JSON with name for the API key
        
    Returns:
        JSON response with new API key (key only shown once)
    """
    try:
        data = api_key_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    # Check if user already has 5 active keys (limit)
    active_keys = APIKey.query.filter_by(user_id=current_user.id, is_active=True).count()
    if active_keys >= 5:
        return jsonify({"error": "Maximum 5 active API keys allowed"}), 400
    
    # Generate new API key
    api_key = APIKey(
        user_id=current_user.id,
        key=generate_api_key(),
        name=data['name']
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    response_data = api_key_response_schema.dump(api_key)
    
    return jsonify({
        "message": "API key created successfully",
        "api_key": response_data,
        "warning": "Save this key securely. It won't be shown again."
    }), 201

@api_bp.route('/keys', methods=['GET'])
@login_required
def list_api_keys():
    """List all API keys for the current user.
    
    Returns:
        JSON response with user's API keys (without key values)
    """
    keys = APIKey.query.filter_by(user_id=current_user.id).order_by(APIKey.created_at.desc()).all()
    
    key_list = []
    for key in keys:
        key_data = api_key_response_schema.dump(key)
        # Don't include the actual key value in list
        key_data.pop('key', None)
        key_list.append(key_data)
    
    return jsonify({
        "api_keys": key_list,
        "total": len(key_list)
    })

@api_bp.route('/keys/<int:key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id):
    """Delete an API key.
    
    Args:
        key_id: ID of API key to delete
        
    Returns:
        JSON response confirming deletion
    """
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    
    if not api_key:
        return jsonify({"error": "API key not found"}), 404
    
    db.session.delete(api_key)
    db.session.commit()
    
    return jsonify({"message": "API key deleted successfully"})

@api_bp.route('/keys/<int:key_id>/toggle', methods=['PUT'])
@login_required
def toggle_api_key(key_id):
    """Toggle API key active status.
    
    Args:
        key_id: ID of API key to toggle
        
    Returns:
        JSON response with updated key status
    """
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    
    if not api_key:
        return jsonify({"error": "API key not found"}), 404
    
    api_key.is_active = not api_key.is_active
    db.session.commit()
    
    status = "activated" if api_key.is_active else "deactivated"
    
    return jsonify({
        "message": f"API key {status} successfully",
        "api_key": {
            "id": api_key.id,
            "name": api_key.name,
            "is_active": api_key.is_active
        }
    })

@api_bp.route('/test', methods=['GET'])
@api_key_required
def test_api_key():
    """Test endpoint to verify API key authentication.
    
    Returns:
        JSON response with authenticated user info
    """
    return jsonify({
        "message": "API key authentication successful",
        "user": {
            "id": g.current_user.id,
            "username": g.current_user.username,
            "role": g.current_user.role
        },
        "api_key": {
            "id": g.api_key.id,
            "name": g.api_key.name,
            "last_used": g.api_key.last_used.isoformat() if g.api_key.last_used else None
        }
    })