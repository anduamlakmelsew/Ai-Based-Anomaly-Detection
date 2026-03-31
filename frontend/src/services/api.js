import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
});

// ✅ ALWAYS attach latest token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.warn("⚠️ No token found for request:", config.url);
    }

    return config;
  },
  (error) => Promise.reject(error),
);

// ✅ HANDLE 401 / 422 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error("API ERROR:", error.response.status, error.response.data);

      // Optional: auto logout if token invalid
      if (error.response.status === 401 || error.response.status === 422) {
        console.warn("🔐 Invalid or missing token");
      }
    }
    return Promise.reject(error);
  },
);

export default api;
