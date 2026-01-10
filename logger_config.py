"""
Logging Configuration Module
=============================

Professional logging system για το HVAC Maintenance App.

Features:
---------
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Logs σε file και console
- Automatic rotation (10MB per file, κρατάει 5 backups)
- Timestamp & module info
- Color-coded console output
- Separate error log file

Usage:
------
    from logger_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("App started")
    logger.error("Something went wrong", exc_info=True)
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

LOG_DIR = "logs"
LOG_FILE = "hvac_app.log"
ERROR_LOG_FILE = "hvac_errors.log"

# Log levels
LOG_LEVEL_FILE = logging.DEBUG      # Everything στο file
LOG_LEVEL_CONSOLE = logging.INFO    # Μόνο INFO+ στο console
LOG_LEVEL_ERROR_FILE = logging.ERROR  # Μόνο errors σε ξεχωριστό file

# Rotation settings
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5  # Κρατάει 5 παλιά files


# ═══════════════════════════════════════════════════════════════════════════
# LOG FORMATS
# ═══════════════════════════════════════════════════════════════════════════

# Detailed format για file
FILE_FORMAT = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Simple format για console
CONSOLE_FORMAT = logging.Formatter(
    fmt='%(levelname)-8s | %(name)s | %(message)s'
)


# ═══════════════════════════════════════════════════════════════════════════
# SETUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def setup_logging():
    """
    Αρχικοποίηση του logging system.
    Καλείται μία φορά στην αρχή του app.
    """
    
    # Create logs directory
    Path(LOG_DIR).mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything
    
    # Clear existing handlers (αν υπάρχουν)
    root_logger.handlers.clear()
    
    # ─────────────────────────────────────────────────────────────────────
    # Handler 1: Main log file (rotating)
    # ─────────────────────────────────────────────────────────────────────
    
    main_file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, LOG_FILE),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    main_file_handler.setLevel(LOG_LEVEL_FILE)
    main_file_handler.setFormatter(FILE_FORMAT)
    root_logger.addHandler(main_file_handler)
    
    # ─────────────────────────────────────────────────────────────────────
    # Handler 2: Error-only log file
    # ─────────────────────────────────────────────────────────────────────
    
    error_file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, ERROR_LOG_FILE),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    error_file_handler.setLevel(LOG_LEVEL_ERROR_FILE)
    error_file_handler.setFormatter(FILE_FORMAT)
    root_logger.addHandler(error_file_handler)
    
    # ─────────────────────────────────────────────────────────────────────
    # Handler 3: Console output
    # ─────────────────────────────────────────────────────────────────────
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL_CONSOLE)
    console_handler.setFormatter(CONSOLE_FORMAT)
    root_logger.addHandler(console_handler)
    
    # ─────────────────────────────────────────────────────────────────────
    # Log startup message
    # ─────────────────────────────────────────────────────────────────────
    
    root_logger.info("=" * 70)
    root_logger.info("HVAC Maintenance System - Logging Started")
    root_logger.info(f"Log directory: {os.path.abspath(LOG_DIR)}")
    root_logger.info(f"Main log: {LOG_FILE}")
    root_logger.info(f"Error log: {ERROR_LOG_FILE}")
    root_logger.info("=" * 70)


def get_logger(name):
    """
    Δημιουργία logger για specific module.
    
    Args:
        name (str): Συνήθως __name__ του module
        
    Returns:
        logging.Logger: Configured logger
        
    Example:
        logger = get_logger(__name__)
        logger.info("Database connected")
    """
    return logging.getLogger(name)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def log_function_call(func):
    """
    Decorator για logging function calls.
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return result
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__}(args={args}, kwargs={kwargs})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}", exc_info=True)
            raise
    
    return wrapper


def log_exception(logger, message="Exception occurred"):
    """
    Helper για logging exceptions με full traceback.
    
    Usage:
        try:
            risky_operation()
        except Exception as e:
            log_exception(logger, "Operation failed")
    """
    logger.error(message, exc_info=True)


def get_log_stats():
    """
    Επιστρέφει statistics για logs.
    
    Returns:
        dict: Log statistics (file sizes, line counts, etc.)
    """
    stats = {
        'main_log': {
            'path': os.path.join(LOG_DIR, LOG_FILE),
            'exists': False,
            'size_kb': 0,
            'lines': 0
        },
        'error_log': {
            'path': os.path.join(LOG_DIR, ERROR_LOG_FILE),
            'exists': False,
            'size_kb': 0,
            'lines': 0
        }
    }
    
    for log_type in ['main_log', 'error_log']:
        path = stats[log_type]['path']
        if os.path.exists(path):
            stats[log_type]['exists'] = True
            stats[log_type]['size_kb'] = os.path.getsize(path) / 1024
            
            with open(path, 'r', encoding='utf-8') as f:
                stats[log_type]['lines'] = sum(1 for _ in f)
    
    return stats


# ═══════════════════════════════════════════════════════════════════════════
# AUTO-INITIALIZATION (Optional)
# ═══════════════════════════════════════════════════════════════════════════

# Αν θέλεις auto-init όταν import-άρεις το module, uncomment:
# setup_logging()

# Αλλιώς, κάλεσε setup_logging() manually στο main.py
