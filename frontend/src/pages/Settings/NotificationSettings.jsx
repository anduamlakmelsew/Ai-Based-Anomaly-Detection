import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import MainLayout from "../../components/layout/MainLayout";
import { getSettingsByCategory, updateSettings } from "../../services/settingsService";

export default function NotificationSettings() {
  const [notifications, setNotifications] = useState({
    email_notifications: true,
    alert_notifications: true,
    report_notifications: false,
    severity_threshold: "MEDIUM",
    notify_on_critical: true,
    notify_on_high: true,
    digest_mode: false,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Load notification settings on mount
  useEffect(() => {
    loadNotificationSettings();
  }, []);

  const loadNotificationSettings = async () => {
    try {
      const response = await getSettingsByCategory("notification");
      if (response.success && response.data) {
        setNotifications(prev => ({
          ...prev,
          ...response.data
        }));
      }
    } catch (err) {
      console.error("Failed to load notification settings:", err);
      setError("Failed to load notification settings");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    
    try {
      const response = await updateSettings(notifications);
      if (response.success) {
        setMessage("Notification preferences saved successfully!");
      } else {
        setError(response.error || "Failed to save notification preferences");
      }
    } catch (err) {
      console.error("Save notification settings error:", err);
      setError(err.response?.data?.error || "Failed to save notification preferences");
    } finally {
      setLoading(false);
      setTimeout(() => {
        setMessage("");
        setError("");
      }, 3000);
    }
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
            <h3 style={{ color: "#3b82f6", marginBottom: "20px" }}>📧 Email Notifications</h3>
            
            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.email_notifications}
                  onChange={(e) => setNotifications({ ...notifications, email_notifications: e.target.checked })}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                Enable Email Notifications
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.alert_notifications}
                  onChange={(e) => setNotifications({ ...notifications, alert_notifications: e.target.checked })}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                Alert Notifications
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.report_notifications}
                  onChange={(e) => setNotifications({ ...notifications, report_notifications: e.target.checked })}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                Report Notifications
              </label>
            </div>

            <h3 style={{ color: "#3b82f6", marginBottom: "20px", marginTop: "30px" }}>🔔 Alert Configuration</h3>
            
            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Severity Threshold:
                <select
                  value={notifications.severity_threshold}
                  onChange={(e) => setNotifications({ ...notifications, severity_threshold: e.target.value })}
                  style={{
                    width: "100%",
                    padding: "12px 16px",
                    background: "rgba(15, 23, 42, 0.8)",
                    border: "1px solid rgba(255,255,255,0.2)",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "14px",
                    marginTop: "8px",
                  }}
                >
                  <option value="LOW">Low and above</option>
                  <option value="MEDIUM">Medium and above</option>
                  <option value="HIGH">High and above</option>
                  <option value="CRITICAL">Critical only</option>
                </select>
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.notify_on_critical}
                  onChange={(e) => setNotifications({ ...notifications, notify_on_critical: e.target.checked })}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                Always Notify on Critical Findings
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.notify_on_high}
                  onChange={(e) => setNotifications({ ...notifications, notify_on_high: e.target.checked })}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                Notify on High Severity Findings
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={notifications.digest_mode}
                  onChange={(e) => setNotifications({ ...notifications, digest_mode: e.target.checked })}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                Digest Mode (Send summary instead of individual alerts)
              </label>
            </div>

            {message && (
              <div style={{ color: "#10b981", marginBottom: "10px" }}>{message}</div>
            )}
            {error && (
              <div style={{ color: "#ef4444", marginBottom: "10px" }}>{error}</div>
            )}

            <motion.button 
              whileHover={{ scale: loading ? 1 : 1.05 }} 
              whileTap={{ scale: loading ? 1 : 0.95 }} 
              type="submit" 
              style={{
                ...buttonStyle,
                opacity: loading ? 0.6 : 1,
              }}
              disabled={loading}
            >
              {loading ? "⏳ Saving..." : "💾 Save Preferences"}
            </motion.button>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
