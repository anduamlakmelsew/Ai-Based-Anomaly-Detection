import { useState } from "react";
import { motion } from "framer-motion";
import MainLayout from "../../components/layout/MainLayout";

export default function SecuritySettings() {
  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage("Passwords do not match");
      return;
    }
    setMessage("Password updated (demo mode)");
    setTimeout(() => setMessage(""), 3000);
    setPasswordData({ currentPassword: "", newPassword: "", confirmPassword: "" });
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
            🔐 Security Settings
          </h2>
        </motion.div>

        <div style={cardStyle}>
          <h3 style={{ marginBottom: "20px" }}>Change Password</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Current Password:
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                  style={inputStyle}
                  required
                />
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                New Password:
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                  style={inputStyle}
                  required
                />
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Confirm New Password:
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                  style={inputStyle}
                  required
                />
              </label>
            </div>

            {message && (
              <div style={{ color: message.includes("not match") ? "#ef4444" : "#10b981", marginBottom: "10px" }}>
                {message}
              </div>
            )}

            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} type="submit" style={buttonStyle}>
              🔑 Update Password
            </motion.button>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
