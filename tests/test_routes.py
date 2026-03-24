import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_todo():
    response = client.post(
        "/todos/",
        json={"task": "Test task", "completed": False}
    )
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["item"]["task"] == "Test task"

def test_update_todo():
    # First create a todo
    create_response = client.post(
        "/todos/",
        json={"task": "Original task", "completed": False}
    )
    todo_id = create_response.json()["id"]

    # Then update it
    update_response = client.put(
        f"/todos/{todo_id}",
        json={"task": "Updated task", "completed": True}
    )
    assert update_response.status_code == 200
    assert update_response.json()["item"]["task"] == "Updated task"
    assert update_response.json()["item"]["completed"] == True

def test_delete_todo():
    # First create a todo
    create_response = client.post(
        "/todos/",
        json={"task": "Task to delete", "completed": False}
    )
    todo_id = create_response.json()["id"]

    # Then delete it
    delete_response = client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == todo_id

    # Verify it's deleted
    get_response = client.put(f"/todos/{todo_id}", json={"task": "Doesn't exist", "completed": False})
    assert get_response.status_code == 404
