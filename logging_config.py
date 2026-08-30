"""
Logging configuration for the Fyyur application.
Sets up structured logging with both file and console handlers.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    """Configure application-wide logging.
    
    Args:
        app: Flask application instance
    """
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Define log format
    log_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10_000_000,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # File handler for errors only
    error_file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10_000_000,  # 10MB
        backupCount=10
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(log_format)
    root_logger.addHandler(error_file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers
    logging.getLogger('flask').setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.info('Logging initialized')
    
    return root_logger
