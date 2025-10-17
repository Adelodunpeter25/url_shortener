"""Database models for URL shortener."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class URL(db.Model):
    """URL model for storing original URLs and their short codes.
    
    Attributes:
        id: Primary key
        original_url: The original long URL
        short_code: Generated short code for the URL
        created_at: Timestamp when the URL was created
        expires_at: Optional expiration timestamp
        click_count: Number of times URL was accessed
    """
    __tablename__ = 'urls'
    
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    click_count = db.Column(db.Integer, default=0)
    
    def is_expired(self):
        """Check if URL has expired."""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        """String representation of URL object."""
        return f'<URL {self.short_code}>'

class ClickAnalytics(db.Model):
    """Model for tracking URL click analytics.
    
    Attributes:
        id: Primary key
        url_id: Foreign key to URL
        clicked_at: Timestamp of click
        ip_address: Visitor IP address
        user_agent: Browser user agent
        referrer: Referring page URL
    """
    __tablename__ = 'click_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(512))
    referrer = db.Column(db.String(2048))
    
    # relationships
    url = db.relationship('URL', backref='clicks')