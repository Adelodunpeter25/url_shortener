"""Marshmallow schemas for request/response validation."""
from marshmallow import Schema, fields, validate

class URLCreateSchema(Schema):
    """Schema for validating URL creation requests.
    
    Fields:
        url: Required valid URL string (1-2048 characters)
        expires_in_days: Optional expiration in days
    """
    url = fields.Url(required=True, validate=validate.Length(min=1, max=2048))
    expires_in_days = fields.Int(validate=validate.Range(min=1, max=365), missing=None)

class BulkURLCreateSchema(Schema):
    """Schema for bulk URL creation requests.
    
    Fields:
        urls: List of URL objects to shorten
    """
    urls = fields.List(fields.Nested(URLCreateSchema), required=True, validate=validate.Length(min=1, max=100))

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
    """
    id = fields.Int()
    original_url = fields.Str()
    short_code = fields.Str()
    short_url = fields.Str()
    created_at = fields.DateTime()
    expires_at = fields.DateTime()
    click_count = fields.Int()