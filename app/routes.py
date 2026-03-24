from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.database import get_db
from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate, TodoResponse

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["todos"])

# CRUD Operations

@router.post("/todos/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """
    Create a new todo item
    """
    try:
        # Create new todo instance
        db_todo = Todo(
            title=todo.title,
            description=todo.description
        )

        # Add to database
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)

        logger.info(f"Created todo with ID: {db_todo.public_id}")
        return db_todo
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create todo item"
        )

@router.get("/todos/", response_model=List[TodoResponse])
def read_todos(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db)
):
    """
    Get all todos with optional filtering and pagination
    """
    try:
        query = db.query(Todo)

        # Apply filter if completed status was provided
        if completed is not None:
            query = query.filter(Todo.completed == completed)

        todos = query.offset(skip).limit(limit).all()
        return todos
    except Exception as e:
        logger.error(f"Error retrieving todos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve todo items"
        )

@router.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(
    todo_id: str = Path(..., title="The public ID of the todo to get"),
    db: Session = Depends(get_db)
):
    """
    Get a specific todo by ID
    """
    try:
        # Query using public_id for security
        todo = db.query(Todo).filter(Todo.public_id == todo_id).first()

        if todo is None:
            logger.warning(f"Todo with ID {todo_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )

        return todo
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving todo {todo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve todo item"
        )

@router.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: str = Path(..., title="The public ID of the todo to update"),
    todo_update: TodoUpdate = None,
    db: Session = Depends(get_db)
):
    """
    Update a todo item
    """
    if todo_update is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )

    try:
        # Query using public_id for security
        db_todo = db.query(Todo).filter(Todo.public_id == todo_id).first()

        if db_todo is None:
            logger.warning(f"Todo with ID {todo_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )

        # Update only the fields that were provided
        update_data = todo_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_todo, key, value)

        # Update the updated_at timestamp
        db_todo.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_todo)

        logger.info(f"Updated todo with ID: {todo_id}")
        return db_todo
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating todo {todo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update todo item"
        )

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: str = Path(..., title="The public ID of the todo to delete"),
    db: Session = Depends(get_db)
):
    """
    Delete a todo item
    """
    try:
        # Query using public_id for security
        db_todo = db.query(Todo).filter(Todo.public_id == todo_id).first()

        if db_todo is None:
            logger.warning(f"Todo with ID {todo_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found"
            )

        db.delete(db_todo)
        db.commit()

        logger.info(f"Deleted todo with ID: {todo_id}")
        return None
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting todo {todo_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete todo item"
        )
