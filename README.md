# URL Shortener

A feature-rich Flask-based URL shortener service with analytics, QR codes, bulk operations, and security features.

## Features

### Core Features
- ✅ URL shortening with Base62 encoding
- ✅ URL redirection with click tracking
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Duplicate prevention
- ✅ URL expiration (1-365 days)

### Advanced Features
- ✅ Bulk URL shortening (up to 100 URLs)
- ✅ Click analytics with detailed tracking
- ✅ QR code generation
- ✅ URL validation and reachability checks
- ✅ Malicious URL detection
- ✅ Rate limiting (10/min for shortening, 100/hour global)

### Security & Performance
- ✅ Input validation with Marshmallow
- ✅ Error handling with proper HTTP codes
- ✅ Environment configuration
- ✅ Comprehensive logging and documentation

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

### Core Endpoints

#### Get API Information
```bash
GET /
```

#### Shorten URL
```bash
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com",
  "expires_in_days": 30  // Optional (1-365 days)
}
```

#### Redirect to Original URL
```bash
GET /<code>
```

### Advanced Endpoints

#### Bulk URL Shortening
```bash
POST /bulk-shorten
Content-Type: application/json

{
  "urls": [
    {"url": "https://example.com", "expires_in_days": 30},
    {"url": "https://google.com"}
  ]
}
```

#### Generate QR Code
```bash
GET /qr/<code>
```
Returns base64 encoded QR code image.

#### Get Analytics
```bash
GET /analytics/<code>
```
Returns click statistics and analytics data.

## Usage Examples

### Basic URL Shortening
```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### URL with Expiration
```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "expires_in_days": 7}'
```

### Bulk Shortening
```bash
curl -X POST http://localhost:5000/bulk-shorten \
  -H "Content-Type: application/json" \
  -d '{"urls": [{"url": "https://example.com"}, {"url": "https://google.com"}]}'
```

### Get QR Code
```bash
curl http://localhost:5000/qr/abc123
```

### View Analytics
```bash
curl http://localhost:5000/analytics/abc123
```

## Response Examples

### Successful URL Shortening
```json
{
  "id": 1,
  "original_url": "https://example.com",
  "short_code": "abc123",
  "short_url": "http://localhost:5000/abc123",
  "created_at": "2024-01-01T12:00:00",
  "expires_at": "2024-01-31T12:00:00",
  "click_count": 0
}
```

### Analytics Response
```json
{
  "short_code": "abc123",
  "original_url": "https://example.com",
  "click_count": 42,
  "created_at": "2024-01-01T12:00:00",
  "expires_at": "2024-01-31T12:00:00",
  "is_expired": false,
  "recent_clicks": 15
}
```

### QR Code Response
```json
{
  "qr_code": "data:image/png;base64,iVBOR...",
  "short_url": "http://localhost:5000/abc123",
  "original_url": "https://example.com"
}
```

## Configuration

### Environment Variables (.env)
```bash
DATABASE_URL=sqlite:///url_shortener.db
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### Rate Limits
- **URL Shortening**: 10 requests per minute per IP
- **Global**: 100 requests per hour per IP
- **Bulk Operations**: Same as single shortening

## Security Features

- **URL Validation**: Checks if URLs are reachable
- **Malicious URL Detection**: Basic blacklist and keyword filtering
- **Rate Limiting**: Prevents abuse and spam
- **Input Validation**: Comprehensive request validation
- **Expiration Handling**: Automatic cleanup of expired URLs

## Analytics Tracking

- **Click Count**: Total clicks per URL
- **Timestamps**: When each click occurred
- **IP Addresses**: Visitor tracking
- **User Agents**: Browser/device information
- **Referrers**: Traffic source tracking
- **Recent Activity**: Last 7 days summary

## Error Handling

- **400**: Invalid URL or validation error
- **404**: Short code not found
- **410**: URL has expired
- **429**: Rate limit exceeded
- **500**: Server/database error

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