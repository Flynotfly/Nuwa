export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatMessageResponse {
  response: string;
}