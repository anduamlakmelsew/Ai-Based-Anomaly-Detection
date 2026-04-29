"""
Centralized logging configuration for the application
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from flask import current_app, request
from datetime import datetime


def setup_logging(app):
    """
    Setup comprehensive logging for the application
    """
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    
    # Create logs directory if not exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # App log file handler
    app_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    app_handler.setFormatter(app_format)
    root_logger.addHandler(app_handler)
    
    # Scan activity log
    scan_handler = RotatingFileHandler(
        os.path.join(log_dir, 'scan.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    scan_handler.setLevel(logging.INFO)
    scan_handler.setFormatter(logging.Formatter(
        '%(asctime)s - SCAN - %(levelname)s - %(message)s'
    ))
    
    scan_logger = logging.getLogger('scan')
    scan_logger.addHandler(scan_handler)
    scan_logger.setLevel(logging.INFO)
    
    # AI prediction log
    ai_handler = RotatingFileHandler(
        os.path.join(log_dir, 'ai.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    ai_handler.setLevel(logging.INFO)
    ai_handler.setFormatter(logging.Formatter(
        '%(asctime)s - AI - %(levelname)s - %(message)s'
    ))
    
    ai_logger = logging.getLogger('ai')
    ai_logger.addHandler(ai_handler)
    ai_logger.setLevel(logging.INFO)
    
    # Authentication log
    auth_handler = RotatingFileHandler(
        os.path.join(log_dir, 'auth.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    auth_handler.setLevel(logging.INFO)
    auth_handler.setFormatter(logging.Formatter(
        '%(asctime)s - AUTH - %(levelname)s - %(message)s - IP: %(ip)s - User: %(user)s'
    ))
    
    auth_logger = logging.getLogger('auth')
    auth_logger.addHandler(auth_handler)
    auth_logger.setLevel(logging.INFO)
    
    # Error log
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10*1024*1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - ERROR - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d] - %(exc_info)s'
    ))
    root_logger.addHandler(error_handler)
    
    app.logger.info(f"Logging setup complete. Log directory: {log_dir}")
    
    return app


def log_scan_activity(scan_id, target, scan_type, status, findings_count=0, user_id=None):
    """Log scan activity"""
    scan_logger = logging.getLogger('scan')
    scan_logger.info(
        f"Scan {scan_id} - {scan_type} on {target} - Status: {status} - "
        f"Findings: {findings_count} - User: {user_id}"
    )


def log_ai_prediction(scan_id, model_type, prediction, confidence, features_count):
    """Log AI prediction"""
    ai_logger = logging.getLogger('ai')
    ai_logger.info(
        f"Scan {scan_id} - Model: {model_type} - Prediction: {prediction} - "
        f"Confidence: {confidence:.2%} - Features: {features_count}"
    )


def log_auth_event(event_type, username, ip_address, success=True, details=None):
    """Log authentication event"""
    auth_logger = logging.getLogger('auth')
    status = "SUCCESS" if success else "FAILED"
    
    extra = {'ip': ip_address, 'user': username}
    
    if details:
        auth_logger.info(
            f"{event_type} - {status} - User: {username} - {details}",
            extra=extra
        )
    else:
        auth_logger.info(
            f"{event_type} - {status} - User: {username}",
            extra=extra
        )


class RequestFormatter(logging.Formatter):
    """Custom formatter to include request info in logs"""
    
    def format(self, record):
        record.url = None
        record.method = None
        record.ip = None
        
        if request:
            record.url = request.path
            record.method = request.method
            record.ip = request.remote_addr
        
        return super().format(record)


def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)
