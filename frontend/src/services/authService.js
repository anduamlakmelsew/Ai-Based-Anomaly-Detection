import axios from "axios";
import api from "./api";

const API = "http://127.0.0.1:5000/api/auth";

// =========================
// 🔐 LOGIN
// =========================
export const login = async (username, password) => {
  try {
    const res = await api.post("/auth/login", { username, password });
    const { access_token, user } = res.data;

    // Store token and user data
    localStorage.setItem("token", access_token);
    localStorage.setItem("user", JSON.stringify(user));

    return { success: true, user, token: access_token };
  } catch (error) {
    console.error("Login error:", error);
    const message = error.response?.data?.error || "Login failed";
    return { success: false, error: message };
  }
};

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/login";
};

export const getToken = () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  // Check if token is expired
  try {
    const tokenData = JSON.parse(atob(token.split('.')[1]));
    const now = Date.now() / 1000;
    if (tokenData.exp && tokenData.exp < now) {
      console.warn("Token expired during getToken check");
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      return null;
    }
    return token;
  } catch (e) {
    console.warn("Invalid token format during getToken check");
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    return null;
  }
};

export const getUser = () => {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
};

export const isAuthenticated = () => {
  return !!getToken();
};

export const refreshToken = async () => {
  try {
    const res = await api.post("/auth/refresh");
    const { access_token } = res.data;
    localStorage.setItem("token", access_token);
    return access_token;
  } catch (error) {
    console.error("Token refresh failed:", error);
    logout();
    return null;
  }
};
