from flask import Blueprint, jsonify, request, current_app
import logging
from typing import Dict, List, Union, Tuple, Any
import json
import os
from models import Todo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for todo routes
todos_bp = Blueprint('todos', __name__)

# In-memory database (for demo purposes)
# In a real application, this would be replaced with a proper database
TODOS_FILE = 'todos.json'

def _load_todos() -> Dict[str, Todo]:
    """Load todos from the JSON file."""
    todos = {}
    try:
        if os.path.exists(TODOS_FILE):
            with open(TODOS_FILE, 'r') as f:
                todos_data = json.load(f)
                for todo_id, todo_data in todos_data.items():
                    todos[todo_id] = Todo.from_dict(todo_data)
    except Exception as e:
        logger.error(f"Error loading todos from file: {str(e)}")
    return todos

def _save_todos(todos: Dict[str, Todo]) -> None:
    """Save todos to the JSON file."""
    try:
        todos_data = {todo_id: todo.to_dict() for todo_id, todo in todos.items()}
        with open(TODOS_FILE, 'w') as f:
            json.dump(todos_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving todos to file: {str(e)}")

# Initialize todos
TODOS = _load_todos()

@todos_bp.route('/todos', methods=['GET'])
def get_todos() -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
    """
    Get all todos.

    Returns:
        JSON response with todos list and HTTP status code
    """
    logger.info("Retrieving all todos")
    try:
        todos_list = [todo.to_dict() for todo in TODOS.values()]
        return jsonify({"todos": todos_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving todos: {str(e)}")
        return jsonify({"error": "Failed to retrieve todos"}), 500

@todos_bp.route('/todos/<string:todo_id>', methods=['GET'])
def get_todo(todo_id: str) -> Union[Tuple[Dict[str, Dict[str, Any]], int], Tuple[Dict[str, str], int]]:
    """
    Get a specific todo by ID.

    Args:
        todo_id (str): ID of the todo to retrieve

    Returns:
        JSON response with todo data or error message and HTTP status code
    """
    logger.info(f"Retrieving todo with ID: {todo_id}")
    try:
        if todo_id in TODOS:
            return jsonify({"todo": TODOS[todo_id].to_dict()}), 200
        else:
            logger.warning(f"Todo with ID {todo_id} not found")
            return jsonify({"error": "Todo not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving todo {todo_id}: {str(e)}")
        return jsonify({"error": f"Failed to retrieve todo: {str(e)}"}), 500

@todos_bp.route('/todos', methods=['POST'])
def create_todo() -> Union[Tuple[Dict[str, Dict[str, Any]], int], Tuple[Dict[str, str], int]]:
    """
    Create a new todo.

    Returns:
        JSON response with created todo data or error message and HTTP status code
    """
    logger.info("Creating new todo")
    try:
        data = request.get_json()

        if not data:
            logger.warning("No JSON data provided")
            return jsonify({"error": "No data provided"}), 400

        if 'title' not in data or not data['title']:
            logger.warning("Missing or empty title in request")
            return jsonify({"error": "Title is required"}), 400

        # Create new todo
        todo = Todo(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False)
        )

        # Add to dictionary
        TODOS[todo.id] = todo

        # Save to file
        _save_todos(TODOS)

        logger.info(f"Successfully created todo with ID: {todo.id}")
        return jsonify({"todo": todo.to_dict()}), 201

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating todo: {str(e)}")
        return jsonify({"error": f"Failed to create todo: {str(e)}"}), 500

@todos_bp.route('/todos/<string:todo_id>', methods=['PUT', 'PATCH'])
def update_todo(todo_id: str) -> Union[Tuple[Dict[str, Dict[str, Any]], int], Tuple[Dict[str, str], int]]:
    """
    Update an existing todo.

    Args:
        todo_id (str): ID of the todo to update

    Returns:
        JSON response with updated todo data or error message and HTTP status code
    """
    logger.info(f"Updating todo with ID: {todo_id}")
    try:
        if todo_id not in TODOS:
            logger.warning(f"Todo with ID {todo_id} not found")
            return jsonify({"error": "Todo not found"}), 404

        data = request.get_json()

        if not data:
            logger.warning("No JSON data provided")
            return jsonify({"error": "No data provided"}), 400

        todo = TODOS[todo_id]

        # Update fields if provided
        if 'title' in data and data['title']:
            todo.title = data['title']
        if 'description' in data:
            todo.description = data['description']
        if 'completed' in data:
            if not isinstance(data['completed'], bool):
                return jsonify({"error": "Completed status must be a boolean"}), 400
            todo.completed = data['completed']

        # Save to file
        _save_todos(TODOS)

        logger.info(f"Successfully updated todo with ID: {todo_id}")
        return jsonify({"todo": todo.to_dict()}), 200

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating todo {todo_id}: {str(e)}")
        return jsonify({"error": f"Failed to update todo: {str(e)}"}), 500

@todos_bp.route('/todos/<string:todo_id>', methods=['DELETE'])
def delete_todo(todo_id: str) -> Union[Tuple[Dict[str, str], int], Tuple[Dict[str, str], int]]:
    """
    Delete a todo.

    Args:
        todo_id (str): ID of the todo to delete

    Returns:
        JSON response with success message or error message and HTTP status code
    """
    logger.info(f"Deleting todo with ID: {todo_id}")
    try:
        if todo_id not in TODOS:
            logger.warning(f"Todo with ID {todo_id} not found")
            return jsonify({"error": "Todo not found"}), 404

        # Delete todo
        del TODOS[todo_id]

        # Save to file
        _save_todos(TODOS)

        logger.info(f"Successfully deleted todo with ID: {todo_id}")
        return jsonify({"message": "Todo deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting todo {todo_id}: {str(e)}")
        return jsonify({"error": f"Failed to delete todo: {str(e)}"}), 500
