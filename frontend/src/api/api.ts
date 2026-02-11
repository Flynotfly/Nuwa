import axios, { AxiosResponse } from "axios";
import {SignInData, TokenResponse, SignUpData, SessionData, ShortUserInfo} from "../auth/types";
import {CharacterFull, CharacterShort, NewCharacterFull} from "../types/character";
import {AnswerType, ChatMessage, ChatTextResponse} from "../types/chatting";
import { getTokens, saveTokens, clearTokens } from "./utils";
import {ChatDetail, ChatListElement} from "../types/chat";
import dayjs from 'dayjs';

const baseURL = import.meta.env.VITE_BASE_URL;

const api = axios.create({
  baseURL: baseURL,
  headers: {
    Accept: 'application/json',
  },
})

const URLs = Object.freeze({
  LOGIN: '/user/login',
  LOGOUT: '/user/logout',
  REGISTER: '/user/register',
  SESSION: '/user/session',
  REFRESH: '/user/refresh',

  CHARACTER: '/characters',
  CHAT: '/chats',
  CHATTING: '/chat',
  IMAGE: '/image',
})

let isRefreshing = false;
let failedQueue: Array<{ resolve: (value?: any) => void; reject: (error?: any) => void }> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.request.use((config) => {
  const { access } = getTokens()
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  if (config.data) {
    config.headers['Content-Type'] = 'application/json'
  }
  return config;
})

api.interceptors.response.use((response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({resolve, reject});
      }).then(() => {
        return api(originalRequest);
      }).catch(err => {
        return Promise.reject(err);
      });
    }
    originalRequest._retry = true;
    isRefreshing = true;
    try {
      await refreshToken();
      const { access } = getTokens();
      processQueue(null, access);
      return api(originalRequest);
    } catch (refreshError) {
      clearTokens();
      processQueue(refreshError, null);
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export function login(data: SignInData): Promise<void> {
  return api.post(URLs.LOGIN, data)
    .then((response) => saveTokens(response.data));
}

export function register(data: SignUpData): Promise<AxiosResponse<void>> {
  return api.post(URLs.REGISTER, data);
}

export function logout(): Promise<void> {
  const { refresh } = getTokens();
  clearTokens();
  return api.post(
    URLs.LOGOUT,
    { refresh },
    {
      validateStatus: (status) => {
        return status >= 200 && status < 300 || status === 401;
      },
    }
  );
}

export function refreshToken(): Promise<void>{
  const { refresh } = getTokens();
  if (!refresh) {
    clearTokens();
    return Promise.reject(new Error('No refresh token available'));
  }
  return api.post(
    URLs.REFRESH,
    { refresh },
  ).then((response) => saveTokens(response.data));
  
}

export function getSession(): Promise<SessionData> {
  return api.get(URLs.SESSION, {
    validateStatus: (status) => {
      return status >= 200 && status < 300;
    },
  }).then((response) => {
    return {
      isAuthenticated: true,
      username: response.data.user.username,
      email: response.data.user.email,
      firstName: response.data.user.firstName,
      lastName: response.data.user.lastName,
      fullName: response.data.user.fullName,
    };
  }).catch((error) => {
    if (error.response?.status === 401) {
      return {
        isAuthenticated: false,
      };
    }
    throw error;
  });
}

// --- Character ---

export function getAllCharacters(only_user?: boolean | null): Promise<CharacterShort[]> {
  const params: Record<string, string> = {};
  if (only_user === true) {
    params.only_user = 'true';
  } else if (only_user === false) {
    params.only_user = 'false';
  }
  return api.get(URLs.CHARACTER, { params })
    .then((response) => response.data);
}

export function getCharacterById(id: number): Promise<CharacterFull> {
  return api.get(URLs.CHARACTER + '/' + id)
    .then((response) => response.data);
}

export function createCharacter(character: NewCharacterFull): Promise<CharacterFull> {
  return api.post(URLs.CHARACTER, character)
    .then((response) => response.data);
}

export function updateCharacter(id: number, character: CharacterFull) {
  return api.put(URLs.CHARACTER + '/' + id, character)
    .then((response) => response.data);
}

export function destroyCharacter(id: number): Promise<void> {
  return api.delete(URLs.CHARACTER + '/' + id)
    .then(() => undefined);
}

// --- Chat and messages---

export function getAllChats(): Promise<ChatListElement[]> {
  return api.get(URLs.CHAT)
    .then((response) => {
      return response.data.map((item: any): ChatListElement => ({
        ...item,
        last_message_datetime: dayjs(item.last_message_datetime)
      }));
    })
}

export function getChatDetail(id: number): Promise<ChatDetail> {
  return api.get(URLs.CHAT + '/' + id)
    .then((response) => response.data)
}

export function createChat(character_id: number): Promise<ChatDetail> {
  return api.post(URLs.CHAT, {character_id})
    .then((response) => response.data)
}

export function getAllMessages(chat_id: number): Promise<ChatMessage[]> {
  return api.get(URLs.CHAT + '/' + chat_id + '/messages')
    .then((response) => {
      return response.data.map((item: any): ChatListElement => ({
        ...item,
        conducted: dayjs(item.last_message_datetime)
      }));
    })
}

// --- Chatting ---

export function sendChatMessage(
  chat_id: number,
  message: string,
  answer_type: AnswerType,
  is_user_message: boolean,
  previous_message_id?: number | null,
): Promise<ChatTextResponse> {
  const payload: Record<string, unknown> = {
    message,
    chat_id,
    answer_type,
    is_user_message,
  };
  if (previous_message_id !== undefined && previous_message_id !== null) {
    payload.previous_message_id = previous_message_id;
  }
  return api.post(URLs.CHATTING, payload)
    .then((response) => {
    const data = response.data;
    if (!Array.isArray(data?.messages)) {
      console.error('Invalid API response:', data);
      throw new Error('API response missing valid messages array');
    }
    const transformedMessages: ChatMessage[] = data.messages.map((msg: any) => {
      return {
        ...msg,
        conducted: dayjs(msg.conducted),
      } as ChatMessage;
    });
    return { messages: transformedMessages };
  }).catch((error) => {
      console.error('Chat message API error:', error);
      throw error;
    });
}
