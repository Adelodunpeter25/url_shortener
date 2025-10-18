"""Admin panel routes for managing users and URLs."""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from core.models import db, User, URL, ClickAnalytics
from core.schemas import UserResponseSchema
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)
user_response_schema = UserResponseSchema()

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def system_stats():
    """Get system-wide statistics.
    
    Returns:
        JSON response with system statistics
    """
    # User statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    
    # URL statistics
    total_urls = URL.query.count()
    anonymous_urls = URL.query.filter_by(user_id=None).count()
    expired_urls = URL.query.filter(URL.expires_at < datetime.utcnow()).count()
    password_protected = URL.query.filter(URL.password.isnot(None)).count()
    
    # Click statistics
    total_clicks = db.session.query(db.func.sum(URL.click_count)).scalar() or 0
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = User.query.filter(User.created_at > week_ago).count()
    recent_urls = URL.query.filter(URL.created_at > week_ago).count()
    recent_clicks = ClickAnalytics.query.filter(ClickAnalytics.clicked_at > week_ago).count()
    
    return jsonify({
        "users": {
            "total": total_users,
            "admins": admin_users,
            "regular": total_users - admin_users,
            "recent": recent_users
        },
        "urls": {
            "total": total_urls,
            "anonymous": anonymous_urls,
            "user_owned": total_urls - anonymous_urls,
            "expired": expired_urls,
            "password_protected": password_protected,
            "recent": recent_urls
        },
        "clicks": {
            "total": total_clicks,
            "recent": recent_clicks,
            "average_per_url": round(total_clicks / total_urls, 2) if total_urls > 0 else 0
        }
    })

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """Get list of all users with statistics.
    
    Returns:
        JSON response with user list and stats
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    user_list = []
    for user in users.items:
        user_data = user_response_schema.dump(user)
        user_data['url_count'] = len(user.urls)
        user_data['total_clicks'] = sum(url.click_count for url in user.urls)
        user_data['role'] = user.role
        user_list.append(user_data)
    
    return jsonify({
        "users": user_list,
        "pagination": {
            "page": page,
            "pages": users.pages,
            "per_page": per_page,
            "total": users.total
        }
    })

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update user role (admin/user).
    
    Args:
        user_id: ID of user to update
        
    Returns:
        JSON response confirming role update
    """
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['user', 'admin']:
        return jsonify({"error": "Invalid role. Must be 'user' or 'admin'"}), 400
    
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin role from self
    if user.id == current_user.id and new_role != 'admin':
        return jsonify({"error": "Cannot remove admin role from yourself"}), 400
    
    user.role = new_role
    db.session.commit()
    
    return jsonify({
        "message": f"User {user.username} role updated to {new_role}",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    })

@admin_bp.route('/urls', methods=['GET'])
@login_required
@admin_required
def list_urls():
    """Get list of all URLs with owner information.
    
    Returns:
        JSON response with URL list
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    
    urls = URL.query.order_by(URL.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    url_list = []
    for url in urls.items:
        url_data = {
            "id": url.id,
            "short_code": url.short_code,
            "original_url": url.original_url,
            "click_count": url.click_count,
            "created_at": url.created_at.isoformat(),
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            "is_expired": url.is_expired(),
            "has_password": bool(url.password),
            "owner": url.owner.username if url.owner else "Anonymous"
        }
        url_list.append(url_data)
    
    return jsonify({
        "urls": url_list,
        "pagination": {
            "page": page,
            "pages": urls.pages,
            "per_page": per_page,
            "total": urls.total
        }
    })

@admin_bp.route('/urls/<code>', methods=['DELETE'])
@login_required
@admin_required
def delete_url(code):
    """Delete any URL (admin privilege).
    
    Args:
        code: Short code of URL to delete
        
    Returns:
        JSON response confirming deletion
    """
    url_obj = URL.query.filter_by(short_code=code).first_or_404()
    
    try:
        # Delete associated analytics
        ClickAnalytics.query.filter_by(url_id=url_obj.id).delete()
        
        # Delete URL
        db.session.delete(url_obj)
        db.session.commit()
        
        return jsonify({
            "message": f"URL {code} deleted successfully",
            "deleted_url": url_obj.original_url
        })
        
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete URL"}), 500