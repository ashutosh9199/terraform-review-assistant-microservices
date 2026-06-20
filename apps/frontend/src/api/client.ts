import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const api = axios.create({
  baseURL
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tra_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setToken(token: string) {
  localStorage.setItem('tra_token', token);
}

export function clearToken() {
  localStorage.removeItem('tra_token');
}

export function hasToken() {
  return Boolean(localStorage.getItem('tra_token'));
}

export function getCurrentUserEmail(): string | undefined {
  const token = localStorage.getItem('tra_token');
  if (!token) return undefined;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub;
  } catch {
    return undefined;
  }
}
