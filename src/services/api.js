import axios from "axios";

const API_URL = "http://localhost:5000/api";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests if it exists
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Authentication services
export const authService = {
  login: async (username, password) => {
    const response = await api.post("/auth/login", { username, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post("/auth/register", userData);
    return response.data;
  },
};

// Admin services
export const adminService = {
  getPendingTeachers: async () => {
    const response = await api.get("/admin/teachers/pending");
    return response.data;
  },

  approveTeacher: async (teacherId) => {
    const response = await api.post(`/admin/teachers/${teacherId}/approve`);
    return response.data;
  },
};

// Teacher services
export const teacherService = {
  createTest: async (testData) => {
    const response = await api.post("/tests", testData);
    return response.data;
  },

  getTests: async (teacherId) => {
    const response = await api.get(`/teachers/${teacherId}/tests`);
    return response.data;
  },

  getTest: async (testId) => {
    const response = await api.get(`/tests/${testId}`);
    return response.data;
  },

  updateTest: async (testId, testData) => {
    const response = await api.put(`/tests/${testId}`, testData);
    return response.data;
  },

  deleteTest: async (testId) => {
    const response = await api.delete(`/tests/${testId}`);
    return response.data;
  },
};

// Student services
export const studentService = {
  getAvailableTests: async () => {
    const response = await api.get("/tests/available");
    return response.data;
  },

  startTest: async (testId, studentId) => {
    const response = await api.post(`/tests/${testId}/start`, {
      student_id: studentId,
    });
    return response.data;
  },

  submitTest: async (attemptId, answers) => {
    const response = await api.post(`/attempts/${attemptId}/submit`, {
      answers,
    });
    return response.data;
  },

  getAttempts: async (studentId) => {
    const response = await api.get(`/students/${studentId}/attempts`);
    return response.data;
  },
};

export default api;
