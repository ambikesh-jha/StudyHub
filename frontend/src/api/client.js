const BASE = "http://localhost:8000";

async function req(method, path, body) {
  const opts = { method, headers: {} };
  if (body) { opts.headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(body); }
  const res = await fetch(BASE + path, opts);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Courses
  getCourses: () => req("GET", "/courses/"),
  createCourse: (data) => req("POST", "/courses/", data),
  updateCourse: (id, data) => req("PUT", `/courses/${id}`, data),
  deleteCourse: (id) => req("DELETE", `/courses/${id}`),

  // Topics
  getTopics: (courseId) => req("GET", `/courses/${courseId}/topics/`),
  createTopic: (courseId, data) => req("POST", `/courses/${courseId}/topics/`, data),
  updateTopic: (courseId, topicId, data) => req("PUT", `/courses/${courseId}/topics/${topicId}`, data),
  deleteTopic: (courseId, topicId) => req("DELETE", `/courses/${courseId}/topics/${topicId}`),

  // Materials
  getMaterials: (topicId) => req("GET", `/topics/${topicId}/materials/`),
  createMaterial: (topicId, data) => req("POST", `/topics/${topicId}/materials/`, data),
  updateMaterial: (topicId, matId, data) => req("PUT", `/topics/${topicId}/materials/${matId}`, data),
  deleteMaterial: (topicId, matId) => req("DELETE", `/topics/${topicId}/materials/${matId}`),

  uploadFile: async (topicId, title, type, file) => {
    const form = new FormData();
    form.append("title", title);
    form.append("type", type);
    form.append("file", file);
    const res = await fetch(`${BASE}/topics/${topicId}/materials/upload`, { method: "POST", body: form });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  fileUrl: (topicId, matId) => `${BASE}/topics/${topicId}/materials/file/${matId}`,
  uploadUrl: (path) => `${BASE}/${path}`,
};
