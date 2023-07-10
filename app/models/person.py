from datetime import datetime
from typing import Optional

from pydantic import BaseModel, root_validator


class Person(BaseModel):
    id: Optional[str]
    identification_id: str
    name: Optional[str]
    team: Optional[str]
    number: Optional[int]
    thumbnail_url: Optional[str]
    status: int
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now()
        return values


class PersonImage(BaseModel):
    id: str
    identification_id: str
    thumbnail_url: str
    name: Optional[str]
    team: Optional[str]
    number: Optional[int]
    percentage: float
    top: float
    left: float
    width: float
    height: float
