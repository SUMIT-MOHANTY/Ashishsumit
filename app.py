from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import logging
from datetime import datetime
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
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(todos_bp)
    
    # Configure static files
    app.static_folder = 'static'
    
    # Initialize database
    db = SQLAlchemy(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), unique=True, nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password_hash = db.Column(db.String(200), nullable=False)
        tasks = db.relationship('Task', backref='user', lazy=True)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        completed = db.Column(db.Boolean, default=False)
        due_date = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"Bad Request: {error}")
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"Not Found: {error}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server Error: {error}")
        return render_template('500.html'), 500

    # Root route for HTML interface
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            # Validate form data
            if not username or not email or not password:
                flash('All fields are required', 'error')
                return render_template('register.html')

            # Check if user already exists
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                flash('Username or email already exists', 'error')
                return render_template('register.html')

            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'error')
                return render_template('register.html')

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                flash('Please provide both username and password', 'error')
                return render_template('login.html')

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
        return render_template('dashboard.html', tasks=tasks)

    @app.route('/tasks/new', methods=['GET', 'POST'])
    @login_required
    def new_task():
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            due_date_str = request.form.get('due_date')

            if not title:
                flash('Title is required', 'error')
                return render_template('new_task.html')

            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

                new_task = Task(
                    title=title,
                    description=description,
                    due_date=due_date,
                    user_id=current_user.id
                )

                db.session.add(new_task)
                db.session.commit()
                flash('Task created successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'error')
                return render_template('new_task.html')

        return render_template('new_task.html')

    @app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(task_id):
        task = Task.query.get_or_404(task_id)

        # Check if task belongs to current user
        if task.user_id != current_user.id:
            abort(403)

        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            due_date_str = request.form.get('due_date')
            completed = 'completed' in request.form

            if not title:
                flash('Title is required', 'error')
                return render_template('edit_task.html', task=task)

            try:
                task.title = title
                task.description = description
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
                task.completed = completed

                db.session.commit()
                flash('Task updated successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'error')
                return render_template('edit_task.html', task=task)

        return render_template('edit_task.html', task=task)

    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    @login_required
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)

        # Check if task belongs to current user
        if task.user_id != current_user.id:
            abort(403)

        try:
            db.session.delete(task)
            db.session.commit()
            flash('Task deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')

        return redirect(url_for('dashboard'))

    @app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
    @login_required
    def toggle_task(task_id):
        task = Task.query.get_or_404(task_id)

        # Check if task belongs to current user
        if task.user_id != current_user.id:
            abort(403)

        try:
            task.completed = not task.completed
            db.session.commit()
            flash(f'Task marked as {"completed" if task.completed else "incomplete"}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')

        return redirect(url_for('dashboard'))
        
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
    
    # Create database tables
    with app.app_context():
        db = SQLAlchemy(app)
        db.create_all()
    
    # Run the app
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
