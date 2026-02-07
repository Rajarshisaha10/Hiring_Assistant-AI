"""
WSGI entry point for production deployment
Usage with gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""

import os
import sys
import logging

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import setup_logging, CONFIG

# Setup logging
logger = setup_logging()

# Import the Flask app
from app import app

if __name__ == "__main__":
    logger.info(f"Starting Hiring Assistant in {os.getenv('FLASK_ENV', 'development')} mode")
    app.run(
        host=CONFIG.HOST,
        port=CONFIG.PORT,
        debug=CONFIG.DEBUG,
        use_reloader=False  # Important: disable reloader in WSGI
    )
