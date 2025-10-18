"""User-specific URL management routes."""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from core.models import db, URL
from core.schemas import URLResponseSchema
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__)
url_response_schema = URLResponseSchema()

@user_bp.route('/my-urls', methods=['GET'])
@login_required
def get_my_urls():
    """Get all URLs owned by current user.
    
    Returns:
        JSON response with user's URLs
    """
    user_urls = []
    
    for url in current_user.urls:
        url_data = url_response_schema.dump(url)
        url_data['short_url'] = f"{request.host_url}{url.short_code}"
        url_data['has_password'] = bool(url.password)
        user_urls.append(url_data)
    
    return jsonify({
        "urls": user_urls,
        "total": len(user_urls)
    })

@user_bp.route('/my-urls/<code>', methods=['DELETE'])
@login_required
def delete_my_url(code):
    """Delete a URL owned by current user.
    
    Args:
        code: Short code of URL to delete
        
    Returns:
        JSON response confirming deletion or error
    """
    url_obj = URL.query.filter_by(short_code=code, user_id=current_user.id).first()
    
    if not url_obj:
        return jsonify({"error": "URL not found or not owned by you"}), 404
    
    try:
        # Delete associated analytics
        from core.models import ClickAnalytics
        ClickAnalytics.query.filter_by(url_id=url_obj.id).delete()
        
        # Delete URL
        db.session.delete(url_obj)
        db.session.commit()
        
        return jsonify({"message": "URL deleted successfully"})
        
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete URL"}), 500

@user_bp.route('/my-urls/<code>/analytics', methods=['GET'])
@login_required
def get_my_url_analytics(code):
    """Get detailed analytics for user's URL.
    
    Args:
        code: Short code of URL to get analytics for
        
    Returns:
        JSON response with detailed analytics
    """
    url_obj = URL.query.filter_by(short_code=code, user_id=current_user.id).first()
    
    if not url_obj:
        return jsonify({"error": "URL not found or not owned by you"}), 404
    
    # Get detailed click analytics
    recent_clicks = []
    for click in url_obj.clicks[-10:]:  # Last 10 clicks
        recent_clicks.append({
            "clicked_at": click.clicked_at.isoformat(),
            "ip_address": click.ip_address,
            "user_agent": click.user_agent[:100] if click.user_agent else None,
            "referrer": click.referrer
        })
    
    return jsonify({
        "url": {
            "short_code": code,
            "original_url": url_obj.original_url,
            "created_at": url_obj.created_at.isoformat(),
            "expires_at": url_obj.expires_at.isoformat() if url_obj.expires_at else None,
            "has_password": bool(url_obj.password)
        },
        "analytics": {
            "total_clicks": url_obj.click_count,
            "is_expired": url_obj.is_expired(),
            "recent_clicks_count": len([c for c in url_obj.clicks if (datetime.utcnow() - c.clicked_at).days < 7]),
            "recent_clicks": recent_clicks
        }
    })

@user_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get comprehensive user statistics.
    
    Returns:
        JSON response with user statistics
    """
    from datetime import datetime
    
    total_urls = len(current_user.urls)
    total_clicks = sum(url.click_count for url in current_user.urls)
    active_urls = len([url for url in current_user.urls if not url.is_expired()])
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_clicks = 0
    
    for url in current_user.urls:
        recent_clicks += len([c for c in url.clicks if c.clicked_at > week_ago])
    
    return jsonify({
        "user": {
            "username": current_user.username,
            "member_since": current_user.created_at.isoformat()
        },
        "statistics": {
            "total_urls": total_urls,
            "active_urls": active_urls,
            "expired_urls": total_urls - active_urls,
            "total_clicks": total_clicks,
            "recent_clicks": recent_clicks,
            "average_clicks_per_url": round(total_clicks / total_urls, 2) if total_urls > 0 else 0
        }
    })