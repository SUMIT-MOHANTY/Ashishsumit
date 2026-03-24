"""
Database models for the Todo application.

This module defines the SQLAlchemy models used in the Todo application.
Currently, it only contains the Todo model for managing todo items.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.hybrid import hybrid_property
import re
import logging

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
    Todo model representing a task in the application.

    Attributes:
        id (int): Primary key for the todo item
        title (str): Description of the todo item (max 200 characters)
        complete (bool): Status of the todo item (True if completed, False otherwise)
        created_at (datetime): Timestamp when the todo item was created
    """

    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _title = db.Column('title', db.String(200), nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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

    def __repr__(self):
        """Return a string representation of the Todo object."""
        return f"<Todo {self.id}: {self.title}>"

    def to_dict(self):
        """
        Convert Todo object to dictionary for API responses.

        Returns:
            dict: Dictionary representation of the Todo object
        """
        return {
            'id': self.id,
            'title': self.title,
            'complete': self.complete,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def create(cls, title, complete=False):
        """
        Create a new Todo item with error handling.

        Args:
            title (str): The title of the todo item
            complete (bool): Whether the todo is complete

        Returns:
            Todo: The created todo object

        Raises:
            ValidationError: If validation fails
            SQLAlchemyError: If database operations fail
        """
        try:
            todo = cls(title=title, complete=complete)
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
