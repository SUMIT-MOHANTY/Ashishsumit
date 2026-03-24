from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Updated TodoBase model with Pydantic V2 syntax
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

    # Use ConfigDict instead of Config class
    model_config = ConfigDict(from_attributes=True)

class TodoCreate(TodoBase):
    pass

class TodoResponse(TodoBase):
    id: int
    created_at: datetime

    # Sample validator using V2 syntax
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title must not be empty')
        return v
