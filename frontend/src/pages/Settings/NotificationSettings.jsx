import { useState } from "react";
import { motion } from "framer-motion";
import MainLayout from "../../components/layout/MainLayout";

export default function NotificationSettings() {
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    reportNotifications: false,
  });
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("Preferences saved (demo mode)");
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
            🔔 Notification Settings
          </h2>
        </motion.div>

        <div style={cardStyle}>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.emailAlerts}
                  onChange={(e) => setNotifications({ ...notifications, emailAlerts: e.target.checked })}
                  style={{ width: "18px", height: "18px" }}
                />
                Email Alerts
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.reportNotifications}
                  onChange={(e) => setNotifications({ ...notifications, reportNotifications: e.target.checked })}
                  style={{ width: "18px", height: "18px" }}
                />
                Report Notifications
              </label>
            </div>

            {message && (
              <div style={{ color: "#10b981", marginBottom: "10px" }}>{message}</div>
            )}

            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} type="submit" style={buttonStyle}>
              💾 Save Preferences
            </motion.button>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
