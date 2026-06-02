import api from "./api";

export const employeeService = {
  list(params = {}) {
    return api.get("/employees", { params });
  },
  get(id) {
    return api.get(`/employees/${id}`);
  },
  getFull(id) {
    return api.get(`/employees/${id}/full`);
  },
  create(data) {
    return api.post("/employees", data);
  },
  update(id, data) {
    return api.put(`/employees/${id}`, data);
  },
  remove(id) {
    return api.delete(`/employees/${id}`);
  },
  uploadDocument(id, documentType, file) {
    const formData = new FormData();
    formData.append("document_type", documentType);
    formData.append("file", file);
    return api.post(`/employees/${id}/documents`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  profile() {
    return api.get("/employees/profile");
  },
};

export function uploadBaseUrl() {
  const base = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
  return base.replace(/\/api\/v1\/?$/, "");
}

export const attendanceService = {
  checkIn() {
    return api.post("/attendance/check-in");
  },
  checkOut() {
    return api.post("/attendance/check-out");
  },
  history() {
    return api.get("/attendance/history");
  },
  today() {
    return api.get("/attendance/today");
  },
  adminList(params = {}) {
    return api.get("/attendance/admin", { params });
  },
};

export const dashboardService = {
  admin() {
    return api.get("/dashboard/admin");
  },
  employee() {
    return api.get("/dashboard/employee");
  },
};

export function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  return error?.message || "Something went wrong";
}
