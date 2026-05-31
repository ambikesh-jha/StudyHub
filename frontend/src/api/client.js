const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API = `${BASE}/api/v1`;
const TOKEN_KEY = "studyhub.tokens";

function readTokens() {
  try {
    return JSON.parse(localStorage.getItem(TOKEN_KEY) || "null");
  } catch {
    return null;
  }
}

function saveTokens(tokens) {
  if (!tokens) localStorage.removeItem(TOKEN_KEY);
  else localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
}

async function req(method, path, body, options = {}) {
  const tokens = readTokens();
  const headers = {};
  let payload = body;

  if (!(body instanceof FormData) && body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  if (tokens?.access_token && options.auth !== false) {
    headers.Authorization = `Bearer ${tokens.access_token}`;
  }

  const res = await fetch(API + path, { method, headers, body: payload });
  if (res.status === 401 && tokens?.refresh_token && options.retry !== false) {
    const refreshed = await refresh(tokens.refresh_token).catch(() => null);
    if (refreshed?.tokens) {
      saveTokens(refreshed.tokens);
      return req(method, path, body, { ...options, retry: false });
    }
  }
  if (!res.ok) throw new Error(await readError(res));
  if (res.status === 204) return null;
  return res.json();
}

async function readError(res) {
  const text = await res.text();
  try {
    const body = JSON.parse(text);
    return body.message || body.detail || body.error || text;
  } catch {
    return text || res.statusText;
  }
}

async function refresh(refreshToken) {
  return req("POST", "/refresh", { refresh_token: refreshToken }, { auth: false, retry: false });
}

function items(response) {
  return Array.isArray(response) ? response : response?.items || [];
}

export const authStore = {
  read: readTokens,
  save: saveTokens,
  clear: () => saveTokens(null),
};

export const api = {
  register: (data) => req("POST", "/register", data, { auth: false }),
  login: (data) => req("POST", "/login", data, { auth: false }),
  refresh,
  logout: (refreshToken) => req("POST", "/logout", { refresh_token: refreshToken }),

  me: () => req("GET", "/users/me"),
  updateMe: (data) => req("PATCH", "/users/me", data),
  stats: () => req("GET", "/users/me/stats"),
  preferences: () => req("GET", "/users/me/preferences"),
  updatePreferences: (data) => req("PATCH", "/users/me/preferences", data),
  changePassword: (data) => req("POST", "/users/me/change-password", data),
  uploadAvatar: (file) => {
    const form = new FormData();
    form.append("file", file);
    return req("POST", "/users/me/avatar", form);
  },

  getCourses: async () => items(await req("GET", "/courses")),
  createCourse: (data) => req("POST", "/courses", data),
  updateCourse: (id, data) => req("PUT", `/courses/${id}`, data),
  deleteCourse: (id) => req("DELETE", `/courses/${id}`),
  shareCourse: (id) => req("GET", `/courses/${id}/share-link`),
  shareLinks: (id) => req("GET", `/courses/${id}/share-links`),
  previewSharedCourse: (token) => req("GET", `/shared/course/${encodeURIComponent(token)}`),
  enrollCourse: (id) => req("POST", `/courses/${id}/enroll`),

  getTopics: async (courseId) => items(await req("GET", `/courses/${courseId}/topics`)),
  createTopic: (courseId, data) => req("POST", `/courses/${courseId}/topics`, data),
  updateTopic: (courseId, topicId, data) => req("PUT", `/courses/${courseId}/topics/${topicId}`, data),
  deleteTopic: (courseId, topicId) => req("DELETE", `/courses/${courseId}/topics/${topicId}`),

  getMaterials: async (topicId) => items(await req("GET", `/courses/topics/${topicId}/materials`)),
  createMaterial: (topicId, data) => req("POST", `/courses/topics/${topicId}/materials`, data),
  updateMaterial: (topicId, matId, data) => req("PUT", `/courses/topics/${topicId}/materials/${matId}`, data),
  deleteMaterial: (topicId, matId) => req("DELETE", `/courses/topics/${topicId}/materials/${matId}`),
  uploadFile: (topicId, title, materialType, file) => {
    const form = new FormData();
    form.append("title", title);
    form.append("material_type", materialType);
    form.append("file", file);
    return req("POST", `/courses/topics/${topicId}/materials/upload`, form);
  },

  uploadUrl: (path) => path?.startsWith("http") ? path : `${BASE}/${path.replace(/^\/+/, "")}`,
};
