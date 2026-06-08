import api from "./api";

export const leaveService = {
  apply: (data) => api.post("/leave/apply", data),
  history: () => api.get("/leave/history"),
  balances: () => api.get("/leave/balances"),
  cancel: (id) => api.post(`/leave/${id}/cancel`),
  pending: () => api.get("/leave/admin/pending"),
  all: (params) => api.get("/leave/admin/all", { params }),
  review: (id, data) => api.patch(`/leave/admin/${id}`, data),
  monthlyReport: (params) => api.get("/leave/reports/monthly", { params }),
  departmentReport: (params) => api.get("/leave/reports/department", { params }),
  employeeReport: (employeeId) => api.get(`/leave/reports/employee/${employeeId}`),
};

export const companySettingsService = {
  get: () => api.get("/company-settings"),
  update: (data) => api.put("/company-settings", data),
  uploadLogo: (formData, config) => api.post("/company-settings/logo", formData, { headers: { "Content-Type": "multipart/form-data" }, ...config }),
};
