# URL Shortener

A feature-rich Flask-based URL shortener service with analytics, QR codes, bulk operations, and security features.

## Features

✅ **Core**: URL shortening, Base62 encoding, expiration, click tracking, SQLite database  
✅ **Advanced**: Bulk operations (100 URLs), QR codes, analytics, password protection  
✅ **User System**: Registration, login, personal dashboards, URL ownership, user management   
✅ **API Access**: API key authentication, programmatic access, multiple auth methods  
✅ **Security**: URL validation, malicious detection, rate limiting, input validation 

## Setup

### 1. Install Dependencies
```bash
uv sync
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Application
```bash
uv run python main.py
```

Server runs on `http://localhost:5000`

## Usage Examples

```bash
# User Registration
curl -X POST http://localhost:5000/auth/register -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'

# User Login
curl -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'

# Basic URL shortening
curl -X POST http://localhost:5000/shorten -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "expires_in_days": 30, "password": "secret"}'

# Bulk shortening
curl -X POST http://localhost:5000/bulk-shorten -H "Content-Type: application/json" \
  -d '{"urls": [{"url": "https://example.com"}, {"url": "https://google.com"}]}'

# User Dashboard
curl -X GET http://localhost:5000/auth/dashboard -H "Cookie: session=<session_cookie>"

# User's URLs
curl -X GET http://localhost:5000/user/my-urls -H "Cookie: session=<session_cookie>"

# Password verification
curl -X POST http://localhost:5000/verify/abc123 -H "Content-Type: application/json" \
  -d '{"password": "secret"}'

# Create API key
curl -X POST http://localhost:5000/api/keys -H "Content-Type: application/json" \
  -H "Cookie: session=<session_cookie>" -d '{"name": "My API Key"}'

# Use API key for URL shortening
curl -X POST http://localhost:5000/shorten -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" -d '{"url": "https://example.com"}'

## Response Examples

**URL Creation**: `{"short_url": "http://localhost:5000/abc123", "has_password": true, "expires_at": "2024-01-31T12:00:00"}`  
**Password Required**: `{"password_required": true, "verify_url": "http://localhost:5000/verify/abc123"}`  
**Analytics**: `{"click_count": 42, "recent_clicks": 15, "is_expired": false}`  
**QR Code**: `{"qr_code": "data:image/png;base64,...", "short_url": "..."}`

## Configuration & Details

**Environment**: Copy `.env.example` to `.env` and configure `DATABASE_URL`, `SECRET_KEY`  

**Database**: SQLite with SQLAlchemy ORM

**Rate Limiting**: Flask-Limiter for IP-based limits

**Validation**: Marshmallow schemas for request/response validation


## Project Structure

```
url_shortener/
├── core/
│   ├── config.py      # Configuration management
│   ├── models.py      # Database models
│   └── schemas.py     # Request/response validation
├── routes/            # API endpoints
├── utils/             # Utility functions
├── main.py            # Application entry point
├── .env.example       # Environment template
└── README.md          # Documentation
```

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Marshmallow**: Serialization/validation
- **Flask-Limiter**: Rate limiting
- **QRCode[PIL]**: QR code generation
- **Requests**: URL validation
- **Werkzeug**: Password hashing
- **Python-dotenv**: Environment management