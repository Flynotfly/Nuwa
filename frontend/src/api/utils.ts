import { TokenResponse } from "../auth/types";

export const getTokens = () => {
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");
  return { access, refresh };
};

export const saveTokens = (tokens: TokenResponse) => {
  localStorage.setItem("access", tokens.access);
  localStorage.setItem("refresh", tokens.refresh);
};

export const clearTokens = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};