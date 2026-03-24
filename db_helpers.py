"""
Database helper functions for reliable database operations.

This module provides functions to ensure reliable database connections,
implement retry logic, and handle connection pooling efficiently.
"""

import time
import logging
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from models import db

logger = logging.getLogger(__name__)

def retry_db_operation(max_retries=3, retry_delay=1):
    """
    Decorator to retry database operations on connection failures.

    Args:
        max_retries (int): Maximum number of retries before failing
        retry_delay (int): Delay in seconds between retries

    Returns:
        function: Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Database operation failed after {max_retries} retries: {str(e)}")
                        raise
                    logger.warning(f"Database operation failed, retrying ({retries}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    # Reset session if needed
                    db.session.rollback()
        return wrapper
    return decorator

def test_connection():
    """
    Test database connectivity.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Execute a simple query to test connection
        db.session.execute("SELECT 1")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False
    finally:
        db.session.rollback()
