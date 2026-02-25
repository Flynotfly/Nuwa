from pydantic import BaseModel


class CharacterRetrieveAll(BaseModel):
    id: int
    name: str
    description: str


class CharacterCreate(BaseModel):
    name: str
    description: str
    system_prompt: str
    is_private: bool
    is_hidden_prompt: bool


class CharacterPartiallyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    is_private: bool | None = None
    is_hidden_prompt: bool | None = None


class CharacterRetrieve(BaseModel):
    id: str
    owner_id: int
    owner_username: str
    name: str
    description: str
    system_prompt: str
    is_private: bool
    is_hidden_prompt: bool

    class Config:
        from_attributes = True
