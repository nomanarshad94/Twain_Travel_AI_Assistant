"""
Entry point for the Travel Advisor Flask application
"""
import os
from src.app import create_app
from src.config import LOG_LEVEL
import logging


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s [line:%(lineno)d] - %(levelname)s - %(message)s'
)

app = create_app()

if __name__ == '__main__':
    app.run(debug=bool(os.getenv("FLASK_DEBUG", "False")), host='0.0.0.0', port=5000)
