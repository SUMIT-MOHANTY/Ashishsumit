"""
Database models for the Todo application.

This module defines the SQLAlchemy models used in the Todo application.
Currently, it only contains the Todo model for managing todo items.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid
import re
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.hybrid import hybrid_property

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance
db = SQLAlchemy()

class ValidationError(Exception):
    """Custom exception for model validation errors."""
    pass

class Todo(db.Model):
    """
    Todo model for representing todo items.

    Attributes:
        id (int): Unique identifier for the todo item
        title (str): Title of the todo item (max 200 characters)
        description (str): Detailed description of the todo item
        complete (bool): Whether the todo item is completed
        created_at (datetime): Timestamp when the todo item was created
        updated_at (datetime): Timestamp when the todo item was last updated
    """

    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _title = db.Column('title', db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @hybrid_property
    def title(self):
        """Getter for title property."""
        return self._title

    @title.setter
    def title(self, value):
        """
        Setter for title property with validation.

        Args:
            value (str): The title value to set

        Raises:
            ValidationError: If the title is invalid
        """
        if not value or not value.strip():
            raise ValidationError("Todo title cannot be empty")

        # Sanitize input - remove any potentially harmful HTML
        value = re.sub(r'<[^>]*>', '', value)

        if len(value) > 200:
            raise ValidationError("Todo title cannot exceed 200 characters")

        self._title = value.strip()

    def __init__(self, title, description=None, complete=False):
        """
        Initialize a new Todo instance.

        Args:
            title (str): Title of the todo item
            description (str, optional): Detailed description of the todo item. Defaults to None.
            complete (bool, optional): Whether the todo item is completed. Defaults to False.
        """
        self.title = title
        self.description = description
        self.complete = complete

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Todo object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the Todo
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'complete': self.complete,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        """
        Create a Todo object from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing todo data

        Returns:
            Todo: New Todo instance
        """
        return cls(
            title=data['title'],
            description=data.get('description'),
            complete=data.get('complete', False)
        )

    @classmethod
    def create(cls, title, description=None, complete=False):
        """
        Create a new Todo item with error handling.

        Args:
            title (str): The title of the todo item
            description (str, optional): Description of the todo item
            complete (bool): Whether the todo is complete

        Returns:
            Todo: The created todo object

        Raises:
            ValidationError: If validation fails
            SQLAlchemyError: If database operations fail
        """
        try:
            todo = cls(title=title, description=description, complete=complete)
            db.session.add(todo)
            db.session.commit()
            return todo
        except ValidationError as e:
            db.session.rollback()
            logger.error(f"Validation error: {str(e)}")
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating todo: {str(e)}")
            raise

    def __str__(self) -> str:
        """String representation of the Todo item."""
        status = "Completed" if self.complete else "Not Completed"
        return f"Todo(id={self.id}, title={self.title}, {status})"

    def __repr__(self) -> str:
        """Return a string representation of the Todo object."""
        return f"<Todo {self.id}: {self.title}>"
