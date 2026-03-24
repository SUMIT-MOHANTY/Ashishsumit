from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class TodoItem(BaseModel):
    task: str
    completed: bool = False

# In-memory database
todos = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up the application")
    yield
    # Shutdown logic
    logger.info("Shutting down the application")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    logger.info("Processing request to read root")
    return {"status": "ok"}

@app.post("/todos/", status_code=201)
async def create_todo(item: TodoItem):
    logger.info(f"Creating todo: {item.task}")
    todo_id = len(todos) + 1
    todos[todo_id] = item
    return {"id": todo_id, "item": item}

@app.put("/todos/{todo_id}", status_code=200)
async def update_todo(todo_id: int, item: TodoItem):
    logger.info(f"Updating todo {todo_id}: {item.task}")
    if todo_id not in todos:
        logger.warning(f"Todo {todo_id} not found")
        raise HTTPException(status_code=404, detail="Todo not found")
    todos[todo_id] = item
    return {"id": todo_id, "item": item}

@app.delete("/todos/{todo_id}", status_code=200)
async def delete_todo(todo_id: int):
    logger.info(f"Deleting todo {todo_id}")
    if todo_id not in todos:
        logger.warning(f"Todo {todo_id} not found")
        raise HTTPException(status_code=404, detail="Todo not found")
    item = todos.pop(todo_id)
    return {"id": todo_id, "item": item}
