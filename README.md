# URL Shortener

A feature-rich Flask-based URL shortener service with analytics, QR codes, bulk operations, and security features.

## Features

✅ **Core**: URL shortening, Base62 encoding, expiration, click tracking, SQLite database  
✅ **Advanced**: Bulk operations (100 URLs), QR codes, analytics, password protection  
✅ **Security**: URL validation, malicious detection, rate limiting, input validation  
✅ **Performance**: Proper error handling, environment config, comprehensive docs

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

## API Endpoints

- `GET /` - API information
- `POST /shorten` - Create short URL
- `GET /<code>` - Redirect to original URL
- `POST /verify/<code>` - Verify password for protected URL
- `POST /bulk-shorten` - Bulk URL shortening
- `GET /qr/<code>` - Generate QR code
- `GET /analytics/<code>` - View click analytics

## Usage Examples

```bash
# Basic shortening
curl -X POST http://localhost:5000/shorten -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "expires_in_days": 30, "password": "secret"}'

# Bulk shortening
curl -X POST http://localhost:5000/bulk-shorten -H "Content-Type: application/json" \
  -d '{"urls": [{"url": "https://example.com"}, {"url": "https://google.com"}]}'

# Password verification
curl -X POST http://localhost:5000/verify/abc123 -H "Content-Type: application/json" \
  -d '{"password": "secret"}'
```

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
├── routes/
│   ├── url_routes.py  # Core URL endpoints
│   └── bulk_routes.py # Bulk operations & features
├── utils/
│   ├── url_generator.py # Base62 code generation
│   ├── validators.py    # URL validation & security
│   └── qr_generator.py  # QR code generation
├── main.py            # Application entry point
├── .env.example       # Environment template
└── README.md          # This file
```

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Marshmallow**: Serialization/validation
- **Flask-Limiter**: Rate limiting
- **QRCode[PIL]**: QR code generation
- **Requests**: URL validation
- **Python-dotenv**: Environment management

## License

MIT License