from pydantic import BaseModel
from datetime import datetime
import uuid


class MediaResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
