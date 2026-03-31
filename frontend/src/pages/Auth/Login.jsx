import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { useTheme } from "../../context/ThemeContext";
import { login as authLogin } from "../../services/authService";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { theme } = useTheme();

  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const darkMode = theme === "dark";

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.username || !form.password) {
      return setError("All fields are required");
    }

    try {
      setLoading(true);

      // Use the shared authService so token handling is consistent.
      const data = await authLogin(form.username, form.password);

      // Flask returns `access_token`
      const token = data.access_token || data.token;
      const userData = data.user;

      if (!token || !userData) {
        return setError(data?.error || "Login failed. Please try again.");
      }

      // Save to AuthContext + localStorage (authService already stores localStorage,
      // but AuthContext keeps the app session state in sync).
      login(userData, token);

      // Navigate to dashboard
      setTimeout(() => navigate("/dashboard"), 100);
    } catch (err) {
      console.error(err);
      const apiError =
        err?.response?.data?.error ||
        err?.response?.data?.message ||
        "Login failed. Please try again.";
      setError(apiError);
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
        onSubmit={handleLogin}
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
        <h2 style={{ textAlign: "center" }}>Login</h2>

        {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}

        <input
          type="text"
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          style={styles.input(darkMode)}
          disabled={loading}
        />

        <div style={{ position: "relative", width: "100%" }}>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            style={{ ...styles.input(darkMode), paddingRight: "40px" }}
            disabled={loading}
          />
          <span
            onClick={() => setShowPassword(!showPassword)}
            style={styles.eye}
          >
            {showPassword ? "🙈" : "👁"}
          </span>
        </div>

        <p style={{ textAlign: "right", fontSize: "13px", margin: 0 }}>
          <Link to="/forgot-password">Forgot Password?</Link>
        </p>

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
          {loading ? "Logging in..." : "Login"}{" "}
          {loading && <span style={styles.spinner}>⏳</span>}
        </button>

        <p style={{ textAlign: "center", fontSize: "14px", marginTop: "10px" }}>
          No account? <Link to="/register">Register</Link>
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
  eye: {
    position: "absolute",
    right: "10px",
    top: "50%",
    transform: "translateY(-50%)",
    cursor: "pointer",
    fontSize: "14px",
    userSelect: "none",
  },
  spinner: {
    marginLeft: "8px",
    fontSize: "14px",
  },
};
