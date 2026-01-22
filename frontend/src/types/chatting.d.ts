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
  user_message: ChatMessage,
  ai_message: ChatMessage,
}
