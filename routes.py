from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Dict, List, Union, Tuple, Any
import json
import os

from models import db, Todo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for todo routes
todos_bp = Blueprint('todos', __name__, url_prefix='')

@todos_bp.route('/todos', methods=['GET'])
def get_todos():
    """Get all todos or filter by completion status"""
    try:
        # Check if we need to filter by completion status
        filter_complete = request.args.get('complete')

        if filter_complete is not None:
            # Convert string to boolean
            is_complete = filter_complete.lower() == 'true'
            todos = Todo.query.filter_by(complete=is_complete).order_by(Todo.created_at.desc()).all()
        else:
            todos = Todo.query.order_by(Todo.created_at.desc()).all()

        return jsonify({
            'success': True,
            'todos': [todo.to_dict() for todo in todos],
            'count': len(todos)
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving todos: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve todos',
            'details': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error retrieving todos: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@todos_bp.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo by ID"""
    try:
        todo = Todo.query.get(todo_id)

        if todo is None:
            return jsonify({
                'success': False,
                'error': f'Todo with ID {todo_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'todo': todo.to_dict()
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving todo {todo_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve todo {todo_id}',
            'details': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error retrieving todo {todo_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@todos_bp.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        # Get data from request
        data = request.get_json()

        # Validate required fields
        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400

        # Validate title is not empty
        title = data.get('title', '').strip()
        if not title:
            return jsonify({
                'success': False,
                'error': 'Title cannot be empty'
            }), 400

        # Get optional fields
        description = data.get('description')
        complete = data.get('complete', False)

        # Create new todo
        new_todo = Todo(
            title=title,
            description=description,
            complete=complete
        )

        # Add to database
        db.session.add(new_todo)
        db.session.commit()

        logger.info(f"Created new todo with ID: {new_todo.id}")

        # Return the created todo
        return jsonify({
            'success': True,
            'todo': new_todo.to_dict(),
            'message': 'Todo created successfully'
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating todo: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create todo',
            'details': str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating todo: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@todos_bp.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a specific todo by ID"""
    try:
        # Get the todo
        todo = Todo.query.get(todo_id)

        if todo is None:
            return jsonify({
                'success': False,
                'error': f'Todo with ID {todo_id} not found'
            }), 404

        # Get data from request
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No update data provided'
            }), 400

        # Update fields if they are provided
        if 'title' in data:
            if not data['title'].strip():
                return jsonify({
                    'success': False,
                    'error': 'Title cannot be empty'
                }), 400
            todo.title = data['title'].strip()

        if 'description' in data:
            todo.description = data['description']

        if 'complete' in data:
            if not isinstance(data['complete'], bool):
                return jsonify({
                    'success': False,
                    'error': '"complete" field must be a boolean value'
                }), 400
            todo.complete = data['complete']

        # Save changes
        db.session.commit()

        logger.info(f"Updated todo with ID: {todo.id}")

        # Return the updated todo
        return jsonify({
            'success': True,
            'todo': todo.to_dict(),
            'message': 'Todo updated successfully'
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating todo {todo_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to update todo {todo_id}',
            'details': str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error updating todo {todo_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@todos_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a specific todo by ID"""
    try:
        # Get the todo
        todo = Todo.query.get(todo_id)

        if todo is None:
            return jsonify({
                'success': False,
                'error': f'Todo with ID {todo_id} not found'
            }), 404

        # Delete the todo
        db.session.delete(todo)
        db.session.commit()

        logger.info(f"Deleted todo with ID: {todo_id}")

        return jsonify({
            'success': True,
            'message': f'Todo with ID {todo_id} deleted successfully'
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error deleting todo {todo_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete todo {todo_id}',
            'details': str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error deleting todo {todo_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

# Bulk operations for efficiency
@todos_bp.route('/todos/bulk', methods=['PUT'])
def bulk_update_todos():
    """Update multiple todos at once"""
    try:
        data = request.get_json()

        if not data or 'todos' not in data or not isinstance(data['todos'], list):
            return jsonify({
                'success': False,
                'error': 'Invalid request format. Expecting {"todos": [{"id": 1, "complete": true}, ...]}'
            }), 400

        updated_count = 0
        not_found = []

        for item in data['todos']:
            if 'id' not in item:
                continue

            todo = Todo.query.get(item['id'])
            if not todo:
                not_found.append(item['id'])
                continue

            if 'complete' in item and isinstance(item['complete'], bool):
                todo.complete = item['complete']
                updated_count += 1

        db.session.commit()

        result = {
            'success': True,
            'updated': updated_count,
            'message': f'Updated {updated_count} todos'
        }

        if not_found:
            result['not_found'] = not_found

        return jsonify(result)

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in bulk update: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update todos',
            'details': str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in bulk update: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500
