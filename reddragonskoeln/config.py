import os

# Configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://reddragons_user:Fbv&?6g/98XxXIL@localhost/reddragons'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
