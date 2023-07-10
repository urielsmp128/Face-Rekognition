from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.person import PersonImage
from app.models.user import UserImage


class Image(BaseModel):
    id: Optional[str]
    identification_id: Optional[str]
    file_name: Optional[str]
    person_count: Optional[int]
    persons: Optional[List[PersonImage]]
    status: int = 2
    error_msg: Optional[str]
    created_at: datetime = datetime.now()
    user: UserImage
