export interface SignInData {
  username: string,
  password: string,
}

export interface TokenResponse {
  access: string,
  refresh: string,
}

export interface SignUpData {
  username: string,
  password: string,
  email: string,
  firstName: string,
  lastName: string,
}

export interface SessionData {
  isAuthenticated: boolean,
  username?: string,
  email?: string,
  firstName?: string,
  lastName?: string,
  fullName?: string,
}

export interface ShortUserInfo {
  id: number,
  username: string,
}
