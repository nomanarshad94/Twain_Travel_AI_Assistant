from flask import Flask, jsonify
import logging
from logging.handlers import RotatingFileHandler
from src.config import LOG_FILE, LOG_LEVEL
from src.app.utils.database import init_connection_pool, init_db
from src.app.utils.constants import (
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_SERVER_ERROR,
    ERROR_INVALID_REQUEST
)


def setup_logging(app):
    """Setup logging configuration"""
    handler = RotatingFileHandler(LOG_FILE, maxBytes=10240000, backupCount=10)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(getattr(logging, LOG_LEVEL))
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, LOG_LEVEL))
    app.logger.info('Travel Advisor application startup')


def create_app():
    """Flask application factory"""
    app = Flask(__name__)

    # Setup logging
    setup_logging(app)

    # Initialize database connection pool and tables
    try:
        init_connection_pool()
        init_db()
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")

    # Register blueprints
    from src.app.routes.chat_routes import chat_bp
    from src.app.routes.main_routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp, url_prefix='/chat')

    # Error handlers
    @app.errorhandler(HTTP_NOT_FOUND)
    def not_found_error(error):
        return jsonify({
            "error": ERROR_INVALID_REQUEST,
            "message": "Resource not found"
        }), HTTP_NOT_FOUND

    @app.errorhandler(HTTP_INTERNAL_SERVER_ERROR)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal error occurred"
        }), HTTP_INTERNAL_SERVER_ERROR

    app.logger.info("Flask app created successfully")
    return app
