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
