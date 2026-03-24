from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Todo title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional todo description")

class TodoCreate(TodoBase):
    @validator('title')
    def title_must_not_be_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Title cannot be empty')
        return v

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

    @validator('title')
    def title_not_empty_if_provided(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Title cannot be empty if provided')
        return v

class TodoResponse(TodoBase):
    id: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
