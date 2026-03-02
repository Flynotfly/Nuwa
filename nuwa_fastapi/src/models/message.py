from datetime import datetime
from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    role: str
    media_type: str
    message: str
    media: str
    conducted: datetime
    history: list
