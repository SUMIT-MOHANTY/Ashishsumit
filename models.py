from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

class Todo(db.Model):
    """
    Todo model for representing todo items.

    Attributes:
        id (int): Unique identifier for the todo item
        title (str): Title of the todo item
        description (str): Detailed description of the todo item
        complete (bool): Whether the todo item is completed
        created_at (datetime): Timestamp when the todo item was created
        updated_at (datetime): Timestamp when the todo item was last updated
    """

    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

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
        self._validate()

    def _validate(self) -> None:
        """Validate the todo item's attributes."""
        if not self.title:
            raise ValueError("Todo title cannot be empty")

        if not isinstance(self.complete, bool):
            raise TypeError("Complete status must be a boolean")

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

    def __str__(self) -> str:
        """String representation of the Todo item."""
        status = "Completed" if self.complete else "Not Completed"
        return f"Todo(id={self.id}, title={self.title}, {status})"

    def __repr__(self) -> str:
        return f"<Todo {self.id}: {self.title}>"
