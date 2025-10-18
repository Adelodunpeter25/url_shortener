"""User authentication routes."""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from core.models import db, User
from core.schemas import UserRegistrationSchema, UserLoginSchema, UserResponseSchema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)
registration_schema = UserRegistrationSchema()
login_schema = UserLoginSchema()
user_response_schema = UserResponseSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account.
    
    Request Body:
        JSON with username, email, and password
        
    Returns:
        JSON response with user data or error
    """
    try:
        data = registration_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    
    try:
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login after registration
        login_user(user)
        
        response_data = user_response_schema.dump(user)
        response_data['url_count'] = len(user.urls)
        
        return jsonify({
            "message": "Registration successful",
            "user": response_data
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with username/email and password.
    
    Request Body:
        JSON with username (or email) and password
        
    Returns:
        JSON response with user data or error
    """
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | 
        (User.email == data['username'])
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    login_user(user)
    
    response_data = user_response_schema.dump(user)
    response_data['url_count'] = len(user.urls)
    
    return jsonify({
        "message": "Login successful",
        "user": response_data
    })

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user.
    
    Returns:
        JSON response confirming logout
    """
    logout_user()
    return jsonify({"message": "Logout successful"})

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Get current user profile.
    
    Returns:
        JSON response with user profile data
    """
    response_data = user_response_schema.dump(current_user)
    response_data['url_count'] = len(current_user.urls)
    
    return jsonify({"user": response_data})

@auth_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Get user dashboard with URL statistics.
    
    Returns:
        JSON response with user URLs and statistics
    """
    from core.schemas import URLResponseSchema
    url_schema = URLResponseSchema()
    
    # Get user's URLs with statistics
    user_urls = []
    total_clicks = 0
    
    for url in current_user.urls:
        url_data = url_schema.dump(url)
        url_data['short_url'] = f"{request.host_url}{url.short_code}"
        url_data['has_password'] = bool(url.password)
        user_urls.append(url_data)
        total_clicks += url.click_count
    
    return jsonify({
        "user": {
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat()
        },
        "statistics": {
            "total_urls": len(user_urls),
            "total_clicks": total_clicks,
            "active_urls": len([u for u in current_user.urls if not u.is_expired()])
        },
        "urls": user_urls
    })