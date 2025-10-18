"""Marshmallow schemas for request/response validation."""
from marshmallow import Schema, fields, validate

class UserRegistrationSchema(Schema):
    """Schema for user registration requests.
    
    Fields:
        username: Required unique username (3-80 characters)
        email: Required valid email address
        password: Required password (6+ characters)
    """
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    """Schema for user login requests.
    
    Fields:
        username: Required username or email
        password: Required password
    """
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserResponseSchema(Schema):
    """Schema for user response data.
    
    Fields:
        id: User ID
        username: Username
        email: Email address
        created_at: Account creation timestamp
        url_count: Number of URLs owned by user
    """
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()
    created_at = fields.DateTime()
    url_count = fields.Int()

class APIKeyCreateSchema(Schema):
    """Schema for API key creation requests.
    
    Fields:
        name: Human-readable name for the API key
    """
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class APIKeyResponseSchema(Schema):
    """Schema for API key response data.
    
    Fields:
        id: API key ID
        name: API key name
        key: API key string (only shown on creation)
        created_at: Creation timestamp
        last_used: Last usage timestamp
        is_active: Whether key is active
    """
    id = fields.Int()
    name = fields.Str()
    key = fields.Str()
    created_at = fields.DateTime()
    last_used = fields.DateTime()
    is_active = fields.Bool()

class URLCreateSchema(Schema):
    """Schema for validating URL creation requests.
    
    Fields:
        url: Required valid URL string (1-2048 characters)
        expires_in_days: Optional expiration in days
        password: Optional password protection
    """
    url = fields.Url(required=True, validate=validate.Length(min=1, max=2048))
    expires_in_days = fields.Int(validate=validate.Range(min=1, max=365), allow_none=True)
    password = fields.Str(validate=validate.Length(min=1, max=255), allow_none=True)

class BulkURLCreateSchema(Schema):
    """Schema for bulk URL creation requests.
    
    Fields:
        urls: List of URL objects to shorten
    """
    urls = fields.List(fields.Nested(URLCreateSchema), required=True, validate=validate.Length(min=1, max=100))

class PasswordValidationSchema(Schema):
    """Schema for password validation requests.
    
    Fields:
        password: Required password string
    """
    password = fields.Str(required=True)

class URLResponseSchema(Schema):
    """Schema for serializing URL response data.
    
    Fields:
        id: URL database ID
        original_url: The original long URL
        short_code: Generated short code
        short_url: Complete shortened URL
        created_at: Creation timestamp
        expires_at: Expiration timestamp
        click_count: Number of clicks
        has_password: Whether URL is password protected
    """
    id = fields.Int()
    original_url = fields.Str()
    short_code = fields.Str()
    short_url = fields.Str()
    created_at = fields.DateTime()
    expires_at = fields.DateTime()
    click_count = fields.Int()
    has_password = fields.Bool()