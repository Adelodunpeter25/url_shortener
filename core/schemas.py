from marshmallow import Schema, fields, validate

class URLCreateSchema(Schema):
    url = fields.Url(required=True, validate=validate.Length(min=1, max=2048))

class URLResponseSchema(Schema):
    id = fields.Int()
    original_url = fields.Str()
    short_code = fields.Str()
    short_url = fields.Str()
    created_at = fields.DateTime()