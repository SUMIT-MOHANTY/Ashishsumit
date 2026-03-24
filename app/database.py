import os
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_database.log')
    ]
)
logger = logging.getLogger(__name__)

# Ensure the data directory exists
def get_db_path():
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    return data_dir / "todos.db"

DB_PATH = get_db_path()

def get_db_connection():
    """Get a connection to the SQLite database with proper error handling"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def initialize_db():
    """Initialize the database with proper error handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create todos table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

# Initialize the database when this module is imported
initialize_db()
