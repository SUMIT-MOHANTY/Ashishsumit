from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from models import db
from routes import todos_bp

def create_app(test_config=None):
    """Create and configure the Flask application"""

    # Initialize Flask app
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///todo_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(todos_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return {
            "message": "Todo API is running",
            "endpoints": {
                "GET /todos": "Get all todos",
                "GET /todos/<id>": "Get a specific todo",
                "POST /todos": "Create a new todo",
                "PUT /todos/<id>": "Update a todo",
                "DELETE /todos/<id>": "Delete a todo",
                "PUT /todos/bulk": "Bulk update todos"
            }
        }

    return app

# This allows the app to be run directly
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

# API endpoint for toggling todo status
@app.route('/toggle/<int:todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    try:
        todo = Todo.query.get_or_404(todo_id)
        data = request.get_json()

        if data and 'completed' in data:
            todo.completed = data['completed']
        else:
            todo.completed = not todo.completed

        db.session.commit()
        return jsonify({'success': True, 'todo': {
            'id': todo.id,
            'title': todo.title,
            'completed': todo.completed
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoint for deleting a todo
@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get_or_404(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Modify add todo route to handle AJAX requests
@app.route('/add', methods=['POST'])
def add():
    try:
        title = request.form.get('title')
        if not title or title.strip() == '':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Todo title cannot be empty'})
            flash('Todo title cannot be empty', 'danger')
            return redirect(url_for('index'))

        todo = Todo(title=title.strip())
        db.session.add(todo)
        db.session.commit()

        # Check if request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'todo': {
                'id': todo.id,
                'title': todo.title,
                'completed': todo.completed
            }})

        flash('Todo added successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'Error adding todo: {str(e)}', 'danger')
        return redirect(url_for('index'))
