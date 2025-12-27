import axios from "axios";

const api = axios.create({
  // Base URL من env مع fallback
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',


  // Timeout (افتراضي 15 ثانية)
  timeout: Number(import.meta.env.VITE_TIMEOUT) || 15000,

  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});
    api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("user_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("user_token");
      // window.location.href = "/login"; // اختياري
    }

    return Promise.reject(error);
  }
);

export default api;

