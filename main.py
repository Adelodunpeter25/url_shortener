"""Flask URL shortener application entry point."""
from flask import Flask
from core.config import Config
from core.models import db
from routes.url_routes import url_bp, limiter
from routes.bulk_routes import bulk_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
limiter.init_app(app)
app.register_blueprint(url_bp)
app.register_blueprint(bulk_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)