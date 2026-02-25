from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ChatCreate(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        serialize_by_alias=True,
    )

    character_id: int = Field(serialization_alias="character")


class ChatUpdate(BaseModel):
    system_prompt: str


class ChatRetrieveAll(BaseModel):
    id: int
    character_id: int = Field(serialization_alias="character")
    character_name: str
    last_message_text: str | None
    last_message_datetime: datetime


class ChatResponse(BaseModel):
    id: int
    owner_id: int = Field(serialization_alias="owner")
    character_id: int = Field(serialization_alias="character")
    character_name: str
    system_prompt: str
    description: str
    is_hidden_prompt: bool
    structure: dict
    last_message_id: int = Field(serialization_alias="last_message")
