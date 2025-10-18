"""Flask URL shortener application entry point."""
from flask import Flask, send_from_directory
from flask_login import LoginManager

from core.config import Config
from core.models import db, User
from routes.url_routes import url_bp, limiter
from routes.bulk_routes import bulk_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp
import json
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
limiter.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Swagger JSON endpoint
@app.route('/swagger.json')
def swagger_json():
    """Serve swagger.json file."""
    return send_from_directory('.', 'swagger.json')

# Swagger UI endpoint
@app.route('/docs/')
def swagger_ui():
    """Serve Swagger UI."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Shortener API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({
                url: '/swagger.json',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ]
            });
        </script>
    </body>
    </html>
    '''

# Register blueprints
app.register_blueprint(url_bp)
app.register_blueprint(bulk_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)