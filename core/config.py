"""Application configuration module."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Flask application configuration class.
    
    Loads configuration from environment variables with fallback defaults.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///url_shortener.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '100 per hour'