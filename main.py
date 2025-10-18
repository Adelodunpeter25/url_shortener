"""Flask URL shortener application entry point."""
from flask import Flask
from flask_login import LoginManager
from core.config import Config
from core.models import db, User
from routes.url_routes import url_bp, limiter
from routes.bulk_routes import bulk_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp

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

# Register blueprints
app.register_blueprint(url_bp)
app.register_blueprint(bulk_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)