import axios from 'axios';

import type { AnalysisMode, HistoryItem, TaskStatus } from '@/types/analysis';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1',
  withCredentials: true,
  timeout: 20000,
});

function readCookie(name: string) {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name.replaceAll('.', '\\.')}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

api.interceptors.request.use((config) => {
  const csrf = readCookie('deepguard_csrf');
  if (csrf) {
    config.headers = config.headers ?? {};
    config.headers['X-CSRF-Token'] = csrf;
  }
  return config;
});

export async function register(email: string, password: string) {
  const response = await api.post('/auth/register', { email, password });
  return response.data as { access_token: string; email: string; user_id: number };
}

export async function login(email: string, password: string) {
  const response = await api.post('/auth/login', { email, password });
  return response.data as { access_token: string; email: string; user_id: number };
}

export async function logout() {
  await api.post('/auth/logout');
}

export async function fetchCurrentUser() {
  const response = await api.get('/auth/me');
  return response.data as { email: string; user_id: number };
}

export async function submitNews(payload: { text?: string; url?: string }) {
  const response = await api.post('/verify/news', payload);
  return response.data as { task_id: string; request_id: string; status: string; message: string };
}

export async function submitFile(mode: Exclude<AnalysisMode, 'news'>, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/verify/${mode}`, formData);
  return response.data as { task_id: string; request_id: string; status: string; message: string };
}

export async function pollResult(taskId: string) {
  const response = await api.get(`/results/${taskId}`);
  return response.data as TaskStatus;
}

export async function fetchHistory() {
  const response = await api.get('/history');
  return response.data as { total: number; results: HistoryItem[] };
}

export function getApiErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (!error.response) {
      return 'Backend unreachable. Start the API and retry.';
    }
  }

  return fallback;
}
