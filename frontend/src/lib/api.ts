import axios from 'axios';

import type { AnalysisMode, HistoryItem, TaskStatus } from '@/types/analysis';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1',
});

export function setToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }
  delete api.defaults.headers.common.Authorization;
}

export async function register(email: string, password: string) {
  const response = await api.post('/auth/register', { email, password });
  return response.data as { access_token: string; email: string; user_id: number };
}

export async function login(email: string, password: string) {
  const response = await api.post('/auth/login', { email, password });
  return response.data as { access_token: string; email: string; user_id: number };
}

export async function submitNews(payload: { text?: string; url?: string }) {
  const response = await api.post('/verify/news', payload);
  return response.data as { task_id: string; request_id: string; status: string; message: string };
}

export async function submitFile(mode: Exclude<AnalysisMode, 'news'>, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/verify/${mode}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
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
