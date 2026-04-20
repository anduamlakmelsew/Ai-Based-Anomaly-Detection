import { useState } from "react";
import { Link } from "react-router-dom";
import { useTheme } from "../../context/ThemeContext";
import api from "../../services/api";

export default function ForgotPassword() {
  const { theme } = useTheme();
  const darkMode = theme === "dark";

  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [tempPassword, setTempPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setTempPassword("");

    if (!email) {
      return setError("Email is required");
    }

    try {
      setLoading(true);
      const response = await api.post("/auth/forgot-password", { email });
      
      if (response.data.success) {
        setSuccess(response.data.message);
        // Show temp password if returned (for demo purposes)
        if (response.data.temp_password) {
          setTempPassword(response.data.temp_password);
        }
        setEmail("");
      } else {
        setError(response.data.message || "Failed to process request.");
      }
    } catch (err) {
      console.error("Forgot password error:", err);
      const message = err.response?.data?.error || err.response?.data?.message || "Failed to send reset instructions. Try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: darkMode ? "#1e293b" : "#f3f4f6",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          width: "360px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          padding: "20px",
          borderRadius: "8px",
          background: darkMode ? "#334155" : "#fff",
          color: darkMode ? "#f1f5f9" : "#111",
        }}
      >
        <h2 style={{ textAlign: "center" }}>Forgot Password</h2>

        {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}
        {success && (
          <p style={{ color: "green", textAlign: "center" }}>{success}</p>
        )}
        {tempPassword && (
          <div style={{
            padding: "15px",
            backgroundColor: darkMode ? "#1e3a5f" : "#dbeafe",
            borderRadius: "8px",
            border: "2px solid #2563eb",
            textAlign: "center"
          }}>
            <p style={{ margin: "0 0 10px 0", fontWeight: "bold", color: darkMode ? "#93c5fd" : "#1e40af" }}>
              Your Temporary Password:
            </p>
            <code style={{
              display: "block",
              padding: "10px",
              backgroundColor: darkMode ? "#0f172a" : "#f3f4f6",
              borderRadius: "4px",
              fontSize: "16px",
              fontFamily: "monospace",
              color: darkMode ? "#f1f5f9" : "#111",
              wordBreak: "break-all"
            }}>
              {tempPassword}
            </code>
            <p style={{ margin: "10px 0 0 0", fontSize: "12px", color: darkMode ? "#94a3b8" : "#6b7280" }}>
              Please copy this password and login immediately. Change it after logging in.
            </p>
          </div>
        )}

        {/* Email */}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={styles.input(darkMode)}
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px",
            backgroundColor: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            position: "relative",
          }}
        >
          {loading ? "Sending..." : "Send Reset Link"}{" "}
          {loading && <span style={styles.spinner}>⏳</span>}
        </button>

        <p style={{ textAlign: "center", fontSize: "14px", marginTop: "10px" }}>
          Remember your password? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  );
}

const styles = {
  input: (darkMode) => ({
    width: "100%",
    padding: "10px 12px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    background: darkMode ? "#475569" : "#fff",
    color: darkMode ? "#f1f5f9" : "#111",
    fontSize: "14px",
    boxSizing: "border-box",
  }),
  spinner: {
    marginLeft: "8px",
    fontSize: "14px",
  },
};
