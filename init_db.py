from app import app, db, User, Task
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        db.create_all()

        # Check if we already have users
        if User.query.count() == 0:
            print("Creating sample user and tasks...")

            # Create a demo user
            demo_user = User(
                username="demo",
                email="demo@example.com",
                password_hash=generate_password_hash("password123")
            )
            db.session.add(demo_user)
            db.session.commit()

            # Create some sample tasks for the demo user
            tasks = [
                Task(
                    title="Welcome to Task Manager",
                    description="This is a sample task to show you how the application works.",
                    due_date=datetime.now() + timedelta(days=1),
                    user_id=demo_user.id
                ),
                Task(
                    title="Create your first task",
                    description="Try creating your own task by clicking the 'Add New Task' button.",
                    due_date=datetime.now() + timedelta(days=2),
                    user_id=demo_user.id
                ),
                Task(
                    title="Mark tasks as complete",
                    description="Click the circle icon to mark a task as complete.",
                    completed=True,
                    user_id=demo_user.id
                )
            ]

            for task in tasks:
                db.session.add(task)

            db.session.commit()
            print("Sample data created successfully!")
        else:
            print("Database already contains users, skipping initialization.")

if __name__ == "__main__":
    init_db()
