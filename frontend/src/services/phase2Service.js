import api from "./api";
import { uploadBaseUrl } from "./crudService";

export { uploadBaseUrl };

export const projectService = {
  list: (params) => api.get("/projects", { params }),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post("/projects", data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  remove: (id) => api.delete(`/projects/${id}`),
};

export const taskService = {
  list: (params) => api.get("/tasks", { params }),
  create: (data) => api.post("/tasks", data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  updateStatus: (id, status) => api.patch(`/tasks/${id}/status`, { status }),
  remove: (id) => api.delete(`/tasks/${id}`),
  comments: (id) => api.get(`/tasks/${id}/comments`),
  addComment: (id, comment) => api.post(`/tasks/${id}/comments`, { comment }),
};

export const announcementService = {
  list: (params) => api.get("/announcements", { params }),
  create: (data) => api.post("/announcements", data),
  update: (id, data) => api.put(`/announcements/${id}`, data),
  remove: (id) => api.delete(`/announcements/${id}`),
};

export const holidayService = {
  list: (params) => api.get("/holidays", { params }),
  create: (data) => api.post("/holidays", data),
  update: (id, data) => api.put(`/holidays/${id}`, data),
  remove: (id) => api.delete(`/holidays/${id}`),
};

export const documentService = {
  list: (params) => api.get("/documents", { params }),
  upload: (formData) => api.post("/documents", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  trackDownload: (id) => api.post(`/documents/${id}/download`),
  remove: (id) => api.delete(`/documents/${id}`),
};

export const expenseService = {
  list: (params) => api.get("/expenses", { params }),
  submit: (formData) => api.post("/expenses", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  review: (id, data) => api.patch(`/expenses/admin/${id}`, data),
  remove: (id) => api.delete(`/expenses/admin/${id}`),
};

export const salaryService = {
  list: (params) => api.get("/salary", { params }),
  get: (id) => api.get(`/salary/${id}`),
  preview: (id) => api.get(`/salary/${id}/preview`),
  download: (id) => api.get(`/salary/${id}/download`, { responseType: "blob" }),
  generate: (data) => api.post("/salary/generate", data),
  update: (id, data) => api.patch(`/salary/${id}`, data),
  regenerate: (id) => api.post(`/salary/${id}/regenerate`),
  markPaid: (id, data) => api.patch(`/salary/${id}/paid`, data),
  remove: (id) => api.delete(`/salary/${id}`),
};

export const auditService = {
  list: (params) => api.get("/audit", { params }),
};
