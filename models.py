from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class Todo:
    """
    Todo model for representing todo items.

    Attributes:
        id (str): Unique identifier for the todo item
        title (str): Title of the todo item
        description (str): Detailed description of the todo item
        completed (bool): Whether the todo item is completed
        created_at (datetime): Timestamp when the todo item was created
    """

    def __init__(
        self,
        title: str,
        description: str,
        completed: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a new Todo instance.

        Args:
            title (str): Title of the todo item
            description (str): Detailed description of the todo item
            completed (bool, optional): Whether the todo item is completed. Defaults to False.
            id (str, optional): Unique identifier. If None, a UUID will be generated.
            created_at (datetime, optional): Creation timestamp. If None, current time is used.
        """
        self.id = id if id else str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = created_at if created_at else datetime.utcnow()

        self._validate()

    def _validate(self) -> None:
        """Validate the todo item's attributes."""
        if not self.title:
            raise ValueError("Todo title cannot be empty")

        if not isinstance(self.completed, bool):
            raise TypeError("Completed status must be a boolean")

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
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
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
        created_at = datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at')

        return cls(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            id=data.get('id'),
            created_at=created_at
        )

    def __str__(self) -> str:
        """String representation of the Todo item."""
        status = "Completed" if self.completed else "Not Completed"
        return f"Todo(id={self.id}, title={self.title}, {status})"

    def __repr__(self) -> str:
        """Detailed string representation of the Todo item."""
        return (f"Todo(id='{self.id}', title='{self.title}', "
                f"description='{self.description}', completed={self.completed}, "
                f"created_at='{self.created_at.isoformat()}')")
