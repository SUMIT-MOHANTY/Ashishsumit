def test_get_todo(client, test_todo):
    """
    Test getting a single todo.
    """
    response = client.get("/todos/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "title" in data

def test_get_todos(client):
    """
    Test getting all todos.
    """
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
