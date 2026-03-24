"""
Flask application initialization for Todo App.

This module initializes the Flask application, configures the database connection,
and ensures the database tables are created if they don't exist.
"""

import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from config import config

def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The configuration to use (development, testing, production)
                           If None, will use environment variable or default

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Determine configuration to use
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    # Apply configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Setup database migrations
    migrate = Migrate(app, db)

    # Create database tables if they don't exist (in development only)
    if app.config.get('DEBUG', False):
        with app.app_context():
            try:
                db.create_all()
                print("Database tables created successfully")
            except Exception as e:
                print(f"Error creating database tables: {e}")

    # Import and register routes (will be implemented in future tasks)
    # from routes import routes_bp
    # app.register_blueprint(routes_bp)

    return app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
