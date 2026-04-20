import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import MainLayout from "../../components/layout/MainLayout";

export default function AdminSettings() {
  const [settings, setSettings] = useState({
    anomaly_threshold: 75,
    scan_interval: 60,
    email_notifications: true,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("Settings saved (demo mode)");
    setTimeout(() => setMessage(""), 3000);
  };

  const cardStyle = {
    background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
    padding: "24px",
    borderRadius: "16px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1)",
    color: "#fff",
    border: "1px solid rgba(255,255,255,0.1)",
  };

  const inputStyle = {
    width: "100%",
    padding: "12px 16px",
    background: "rgba(15, 23, 42, 0.8)",
    border: "1px solid rgba(255,255,255,0.2)",
    borderRadius: "8px",
    color: "#fff",
    fontSize: "14px",
    marginTop: "8px",
  };

  const buttonStyle = {
    padding: "12px 24px",
    background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
    marginTop: "20px",
  };

  return (
    <MainLayout>
      <div style={{ color: "#fff", paddingBottom: "50px" }}>
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h2 style={{
            marginBottom: "10px",
            fontSize: "2rem",
            fontWeight: "bold",
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}>
            ⚙️ Admin Settings
          </h2>
        </motion.div>

        <div style={cardStyle}>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Default Scan Interval (minutes):
                <input
                  type="number"
                  value={settings.scan_interval}
                  onChange={(e) => setSettings({ ...settings, scan_interval: e.target.value })}
                  style={inputStyle}
                />
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Anomaly Threshold (%):
                <input
                  type="number"
                  value={settings.anomaly_threshold}
                  onChange={(e) => setSettings({ ...settings, anomaly_threshold: e.target.value })}
                  style={inputStyle}
                />
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={settings.email_notifications}
                  onChange={(e) => setSettings({ ...settings, email_notifications: e.target.checked })}
                  style={{ width: "18px", height: "18px" }}
                />
                Email Notifications
              </label>
            </div>

            {message && (
              <div style={{ color: "#10b981", marginBottom: "10px" }}>{message}</div>
            )}

            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} type="submit" style={buttonStyle}>
              💾 Save System Settings
            </motion.button>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
