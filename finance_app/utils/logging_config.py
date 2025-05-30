import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app_name='finance_app'):
    """Set up logging configuration
    
    Args:
        app_name (str): Name of the application
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file path
    log_file = os.path.join(log_dir, f'{app_name}.log')
    
    # Logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler with UTF-8 encoding
    if sys.platform == 'win32':
        # On Windows, use sys.stdout with UTF-8 encoding
        console_handler = logging.StreamHandler(sys.stdout)
    else:
        console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # App logger
    app_logger = logging.getLogger(app_name)
    app_logger.setLevel(logging.DEBUG)
    
    return app_logger 