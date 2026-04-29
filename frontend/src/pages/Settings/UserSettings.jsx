import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useAuth } from "../../contexts/AuthProvider";
import MainLayout from "../../components/layout/MainLayout";
import { getProfile, updateProfile } from "../../services/settingsService";

export default function UserSettings() {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState({
    username: "",
    email: "",
    role: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Fetch profile from API
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await getProfile();
        if (response.success && response.data) {
          setProfile({
            username: response.data.username || "",
            email: response.data.email || "",
            role: response.data.role || "",
          });
        }
      } catch (err) {
        console.error("Failed to fetch profile:", err);
        setError("Failed to load profile data");
      }
    };
    
    fetchProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    
    try {
      const response = await updateProfile({ email: profile.email });
      if (response.success) {
        setMessage("Profile updated successfully!");
        // Refresh auth context to get updated user data
        if (refreshUser) {
          await refreshUser();
        }
      } else {
        setError(response.error || "Failed to update profile");
      }
    } catch (err) {
      console.error("Update profile error:", err);
      setError(err.response?.data?.error || "Failed to update profile");
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
            👤 User Settings
          </h2>
        </motion.div>

        <div style={cardStyle}>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Username:
                <input
                  type="text"
                  value={profile.username}
                  disabled
                  style={{ ...inputStyle, opacity: 0.6 }}
                />
              </label>
              <small style={{ color: "#64748b" }}>Username cannot be changed</small>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Email:
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  placeholder="Enter your email"
                  style={inputStyle}
                />
              </label>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <label style={{ color: "#94a3b8" }}>
                Role:
                <input
                  type="text"
                  value={profile.role}
                  disabled
                  style={{ ...inputStyle, opacity: 0.6 }}
                />
              </label>
              <small style={{ color: "#64748b" }}>Role can only be changed by admin</small>
            </div>

            {message && (
              <div style={{ color: "#10b981", marginBottom: "10px" }}>{message}</div>
            )}
            {error && (
              <div style={{ color: "#ef4444", marginBottom: "10px" }}>{error}</div>
            )}

            <motion.button 
              whileHover={{ scale: 1.05 }} 
              whileTap={{ scale: 0.95 }} 
              type="submit" 
              style={buttonStyle}
              disabled={loading}
            >
              {loading ? "⏳ Saving..." : "💾 Save Changes"}
            </motion.button>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}
