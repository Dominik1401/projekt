from flask import Flask, render_template
from frontend.routes import frontend_bp
from backend.routes import backend_bp
from backend.models import db
from dotenv import load_dotenv
from flask_talisman import Talisman
from logging.handlers import RotatingFileHandler
import os
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder=None)

# Apply configuration
app.config.from_object('config.DevelopmentConfig')

# Check if SECRET_KEY is set
if not app.secret_key:
    raise ValueError("SECRET_KEY is not set in the environment variables.")
    
db.init_app(app)

# Security headers
Talisman(app)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Blueprint registration
app.register_blueprint(frontend_bp)
app.register_blueprint(backend_bp)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
    
# Ensure database tables are created
with app.app_context():
    db.create_all()

# Create a logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.mkdir('logs')

# Configure logging
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# Log app startup
app.logger.info('App startup')

# Run application
if __name__ == '__main__':
    app.run()
    
