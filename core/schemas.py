"""Marshmallow schemas for request/response validation."""
from marshmallow import Schema, fields, validate

class URLCreateSchema(Schema):
    """Schema for validating URL creation requests.
    
    Fields:
        url: Required valid URL string (1-2048 characters)
    """
    url = fields.Url(required=True, validate=validate.Length(min=1, max=2048))

class URLResponseSchema(Schema):
    """Schema for serializing URL response data.
    
    Fields:
        id: URL database ID
        original_url: The original long URL
        short_code: Generated short code
        short_url: Complete shortened URL
        created_at: Creation timestamp
    """
    id = fields.Int()
    original_url = fields.Str()
    short_code = fields.Str()
    short_url = fields.Str()
    created_at = fields.DateTime()