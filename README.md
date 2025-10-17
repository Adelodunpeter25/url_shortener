# URL Shortener

A simple Flask-based URL shortener service.

## Setup

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

## API

- `POST /shorten` - Create short URL
- `GET /<code>` - Redirect to original URL

### Example

```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```