from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class EventIn(BaseModel):
    source: Optional[str] = Field(default=None, max_length=200)
    payload: Dict[str, Any]

class EventOut(BaseModel):
    id: int
    received_at: str
    source: Optional[str]
    payload: Dict[str, Any]
