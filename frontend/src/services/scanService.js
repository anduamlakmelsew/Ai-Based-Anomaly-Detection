import api from "./api";

// 🚀 Start scan
export const startScan = async (data) => {
  try {
    // `api` automatically injects `Authorization: Bearer <token>` via interceptor.
    const res = await api.post("/scan/start", data);
    return res.data;
  } catch (err) {
    console.error("Scan error:", err);
    throw err;
  }
};

// 📜 Get history
export const getScanHistory = async () => {
  try {
    const res = await api.get("/scan/history");
    return res.data;
  } catch (err) {
    console.error("History error:", err);
    throw err;
  }
};

// 🔍 GET SINGLE SCAN (🔥 NEW)
export const getScanById = async (id) => {
  try {
    const res = await api.get(`/scan/${id}`);
    return res.data;
  } catch (err) {
    console.error("Get scan error:", err);
    throw err;
  }
};

// 🌐 Network discovery
export const discoverHosts = async (targetRange) => {
  try {
    const res = await api.post("/scan/discover", { target: targetRange });
    return res.data;
  } catch (err) {
    console.error("Discover error:", err);
    throw err;
  }
};
