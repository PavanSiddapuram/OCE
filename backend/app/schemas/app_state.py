from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AppStateIn(BaseModel):
    value: Any


class AppStateOut(BaseModel):
    key: str
    value: Any
    updated_at: datetime

    model_config = {"from_attributes": True}
