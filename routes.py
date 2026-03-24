"""
Routes for the Todo application.

This module defines all the API endpoints for handling CRUD operations
on Todo items and rendering template pages.
"""

from flask import Blueprint, request, jsonify, render_template, abort, current_app
from sqlalchemy.exc import SQLAlchemyError
from models import db, Todo, ValidationError
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
todo_bp = Blueprint('todo', __name__)

@todo_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle validation errors from models."""
    return jsonify(error=str(e)), 400

@todo_bp.errorhandler(SQLAlchemyError)
def handle_database_error(e):
    """Handle database errors."""
    logger.error(f"Database error: {str(e)}")
    return jsonify(error="Database operation failed. Please try again later."), 500

@todo_bp.route('/api/todos', methods=['GET'])
def get_todos():
    """API endpoint to get all todos."""
    try:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
        return jsonify([todo.to_dict() for todo in todos])
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving todos: {str(e)}")
        return jsonify(error="Database error"), 500

@todo_bp.route('/api/todos', methods=['POST'])
def create_todo():
    """API endpoint to create a new todo item."""
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify(error="Title is required"), 400

    try:
        todo = Todo.create(title=data['title'], complete=data.get('complete', False))
        return jsonify(todo.to_dict()), 201
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    except SQLAlchemyError as e:
        logger.error(f"Error creating todo: {str(e)}")
        return jsonify(error="Database error"), 500
