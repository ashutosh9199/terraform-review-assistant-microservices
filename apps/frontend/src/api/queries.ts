import { api } from './client';
import type { DashboardSummary, LlmSettings, LlmTestResult, Project, Review } from './types';

export async function login(email: string, password: string) {
  const { data } = await api.post('/api/auth/login', { email, password });
  return data as { access_token: string; roles: string[] };
}

export async function signup(email: string, password: string, fullName?: string) {
  const { data } = await api.post('/api/auth/signup', { email, password, full_name: fullName || undefined });
  return data as { access_token: string; roles: string[] };
}

export async function getDashboard() {
  const { data } = await api.get('/api/dashboard/summary');
  return data as DashboardSummary;
}

export async function getProjects() {
  const { data } = await api.get('/api/projects');
  return data as Project[];
}

export async function createProject(name: string, description?: string) {
  const { data } = await api.post('/api/projects', { name, description });
  return data as Project;
}

export async function uploadReview(projectId: number, files: File[]) {
  const form = new FormData();
  files.forEach((file) => form.append('files', file));
  if (files[0]) {
    form.append('file', files[0]);
  }
  const { data } = await api.post(`/api/reviews/upload?project_id=${projectId}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data as Review;
}

export async function getReview(id: number) {
  const { data } = await api.get(`/api/reviews/${id}`);
  return data as Review;
}

export async function getLlmSettings() {
  const { data } = await api.get('/api/settings/llm');
  return data as LlmSettings | null;
}

export async function saveLlmSettings(payload: {
  api_key: string;
  endpoint?: string;
  model?: string;
  provider?: string;
}) {
  const { data } = await api.put('/api/settings/llm', payload);
  return data as LlmSettings;
}

export async function testLlmSettings(payload: {
  api_key: string;
  endpoint?: string;
  model?: string;
  provider?: string;
}) {
  const { data } = await api.post('/api/settings/llm/test', payload);
  return data as LlmTestResult;
}

export async function deleteLlmSettings() {
  await api.delete('/api/settings/llm');
}
