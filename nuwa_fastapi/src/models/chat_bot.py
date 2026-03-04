from pydantic import BaseModel


class ChatPayload(BaseModel):
    chat_id: int
    user_input: str | None = None
    previous_message_id: int | None = None
    is_user_message: bool = False
    stream: bool = False
    answer_type: str = "detect"
