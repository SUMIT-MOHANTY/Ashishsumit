from flask import Flask, jsonify, render_template
from flask_cors import CORS
import logging
import os
from routes import todos_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(todos_bp)

    # Configure static files
    app.static_folder = 'static'

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"Bad Request: {error}")
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"Not Found: {error}")
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server Error: {error}")
        return jsonify({"error": "Internal Server Error", "message": str(error)}), 500

    # Root route for HTML interface
    @app.route('/')
    def index():
        return render_template('index.html')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200

    # Print routes for debugging
    @app.before_first_request
    def log_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": sorted([method for method in rule.methods if method not in ('HEAD', 'OPTIONS')]),
                "path": str(rule)
            })
        logger.info(f"Registered routes: {routes}")

    return app

if __name__ == '__main__':
    app = create_app()

    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))

    # Run the app
    logger.info(f"Starting Todo API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
