import { useState } from "react";
import { Link } from "react-router-dom";
import { useTheme } from "../../context/ThemeContext";

export default function ForgotPassword() {
  const { theme } = useTheme();
  const darkMode = theme === "dark";

  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!email) {
      return setError("Email is required");
    }

    try {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1200)); // simulate API
      setSuccess("Password reset instructions sent to your email.");
      setEmail("");
    } catch {
      setError("Failed to send reset instructions. Try again.");
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
