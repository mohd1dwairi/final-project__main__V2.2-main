from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class ModelBase(BaseModel):
    name: str
    version: str
    path: Optional[str] = None
    params: Optional[Dict] = None
    metrics: Optional[Dict] = None
    is_active: Optional[bool] = True


class ModelResponse(ModelBase):
    id: int
    registered_at: datetime

    class Config:
        from_attributes = True
