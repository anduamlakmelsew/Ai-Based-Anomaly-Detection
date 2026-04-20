import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
});

// ✅ ALWAYS attach latest token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      // Check if token is expired (simple check)
      try {
        const tokenData = JSON.parse(atob(token.split('.')[1]));
        const now = Date.now() / 1000;
        if (tokenData.exp && tokenData.exp < now) {
          console.warn("🔐 Token expired, removing from storage");
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          // Redirect to login
          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
          return Promise.reject(new Error("Token expired"));
        }
        config.headers.Authorization = `Bearer ${token}`;
      } catch (e) {
        console.warn("🔐 Invalid token format, removing from storage");
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
        return Promise.reject(new Error("Invalid token"));
      }
    } else {
      console.warn("⚠️ No token found for request:", config.url);
      // Only redirect to login if not already on login page and this is a protected route
      const publicAuthEndpoints = ["/auth/login", "/auth/register"];
      const isPublicEndpoint = publicAuthEndpoints.some(endpoint => config.url.includes(endpoint));
      if (window.location.pathname !== "/login" && !isPublicEndpoint) {
        window.location.href = "/login";
      }
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

      // Auto logout on 401/422 and clear storage
      if (error.response.status === 401 || error.response.status === 422) {
        console.warn("🔐 Authentication failed, clearing session");
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        
        // Only redirect if not already on login page
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  },
);

export default api;
