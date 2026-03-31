import axios from "axios";

const API = "http://127.0.0.1:5000/api/auth";

// =========================
// 🔐 LOGIN
// =========================
export const login = async (username, password) => {
  const res = await axios.post(`${API}/login`, {
    username,
    password,
  });

  const data = res.data;

  // ✅ SAVE TOKEN (support both `access_token` and legacy/alternate `token`)
  const token = data.access_token || data.token;
  if (token) {
    localStorage.setItem("token", token);
  }
  if (data.user) {
    localStorage.setItem("user", JSON.stringify(data.user));
  }

  return data;
};

// =========================
// 🚪 LOGOUT
// =========================
export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};

// =========================
// 🔑 GET TOKEN
// =========================
export const getToken = () => {
  return localStorage.getItem("token");
};
