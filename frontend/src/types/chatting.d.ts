import {Dayjs} from "dayjs";

export interface ChatMessage {
  id: number,
  role: 'user' | 'assistant',
  media_type: 'text' | 'image' | 'video',
  message: string,
  media: string,
  conducted: Dayjs,
  history: Array<number>,
}

export interface ChatTextResponse {
  messages: ChatMessage[],
}

export type AnswerType =
  'text'
  | 'image'
  | 'video';
