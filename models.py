from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

class Todo(db.Model):
    """Todo model representing a task in the todo list"""

    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, title, description=None, complete=False):
        self.title = title
        self.description = description
        self.complete = complete

    def to_dict(self):
        """Convert Todo object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'complete': self.complete,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Todo {self.id}: {self.title}>"
