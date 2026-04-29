import api from "./api";

/**
 * AI Security Service
 * Handles all AI-related API calls for the AI Security Lab
 */

// 🧠 Run manual AI test
export const runAIManualTest = async (data) => {
  try {
    const res = await api.post("/scan/ai/test", data);
    return res.data;
  } catch (err) {
    console.error("AI manual test error:", err);
    throw err;
  }
};

// 📜 Get AI detection history
export const getAIDetectionHistory = async (limit = 100, sourceType = null) => {
  try {
    const params = new URLSearchParams();
    if (limit) params.append("limit", limit);
    if (sourceType) params.append("source_type", sourceType);
    
    const res = await api.get(`/scan/history/ai?${params.toString()}`);
    return res.data;
  } catch (err) {
    console.error("AI detection history error:", err);
    throw err;
  }
};

// 📊 Get AI detection statistics
export const getAIDetectionStats = async (hours = 24) => {
  try {
    const res = await api.get(`/scan/history/ai/stats?hours=${hours}`);
    return res.data;
  } catch (err) {
    console.error("AI detection stats error:", err);
    throw err;
  }
};

/**
 * Default input templates for AI testing
 */
export const getNetworkTemplate = () => ({
  duration: 1.5,
  src_bytes: 1024,
  dst_bytes: 2048,
  protocol: "tcp",
  packet_count: 10,
  src_port: 54321,
  dst_port: 80,
  syn_flag: 1,
  ack_flag: 1,
  rst_flag: 0,
  fin_flag: 0
});

export const getSystemTemplate = () => ({
  cpu_usage: 45.5,
  memory_usage: 60.2,
  disk_usage: 55.0,
  open_ports: 12,
  process_count: 150,
  suspicious_processes: 0,
  user_count: 2,
  admin_count: 1,
  service_count: 10,
  exposed_services: 2,
  total_vulns: 3,
  critical_vulns: 0,
  high_vulns: 1,
  firewall_enabled: 1
});

export const getWebTemplate = () => ({
  url: "/api/search?q=test",
  payload: "<script>alert('xss')</script>",
  method: "POST",
  headers: {},
  status_code: 200
});
