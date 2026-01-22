import {Dayjs} from "dayjs";

export interface ChatListElement {
  id: number,
  character: number,
  character_name: string,
  last_message_text: string,
  last_message_datetime: Dayjs
}

export interface ChatDetail {
  id: number,
  owner: number,
  character: number,
  character_name: string,
  system_prompt: string,
  description: string,
  is_hidden_prompt: boolean,
  structure: object,
  last_message: number,
}
