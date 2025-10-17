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
    """
    __tablename__ = 'urls'
    
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """String representation of URL object."""
        return f'<URL {self.short_code}>'