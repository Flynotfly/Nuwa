export interface CharacterShort {
  id: number,
  name: string,
  description: string,
}

export interface NewCharacterFull {
  name: string,
  description: string,
  system_prompt: string,
  is_private: boolean,
  is_hidden_prompt: boolean,
}

export interface CharacterFull extends NewCharacterFull {
  id: number,
  owner: number,
  owner_username: string,
}
