from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import Todo

# Set up in-memory SQLite for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database and tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_todo():
    response = client.post(
        "/todos/",
        json={"title": "Test Todo", "description": "Test description"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test description"
    assert "id" in data
    todo_id = data["id"]

    # Verify the todo was created
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Todo"

def test_create_todo_invalid():
    response = client.post(
        "/todos/",
        json={"title": "", "description": "Test description"},
    )
    assert response.status_code == 422  # Validation error

def test_read_todos():
    # Create test todos
    client.post("/todos/", json={"title": "Todo 1"})
    client.post("/todos/", json={"title": "Todo 2"})

    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Test pagination
    response = client.get("/todos/?skip=0&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_update_todo():
    # Create a todo to update
    response = client.post(
        "/todos/",
        json={"title": "Original Title"},
    )
    todo_id = response.json()["id"]

    # Update it
    response = client.patch(
        f"/todos/{todo_id}",
        json={"title": "Updated Title", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] == True

def test_delete_todo():
    # Create a todo to delete
    response = client.post(
        "/todos/",
        json={"title": "Delete Me"},
    )
    todo_id = response.json()["id"]

    # Delete it
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 404
