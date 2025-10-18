"""Database models for URL shortener."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and URL ownership.
    
    Attributes:
        id: Primary key
        username: Unique username
        email: User email address
        password_hash: Hashed password
        created_at: Account creation timestamp
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to URLs
    urls = db.relationship('URL', backref='owner', lazy=True)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """String representation of User object."""
        return f'<User {self.username}>'

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
    password = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Allow anonymous URLs
    
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