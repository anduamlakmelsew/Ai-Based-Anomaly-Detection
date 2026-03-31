import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { useTheme } from "../../context/ThemeContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { theme } = useTheme();

  const [form, setForm] = useState({
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const darkMode = theme === "dark";

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.username || !form.password || !form.confirmPassword) {
      return setError("All fields are required");
    }
    if (form.password !== form.confirmPassword) {
      return setError("Passwords do not match");
    }

    try {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1200)); // simulate API
      register({ username: form.username, role: "admin" });
      navigate("/dashboard");
    } catch {
      setError("Registration failed. Please try again.");
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
        onSubmit={handleRegister}
        style={{
          width: "360px", // fixed width for perfect alignment
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          padding: "20px",
          borderRadius: "8px",
          background: darkMode ? "#334155" : "#fff",
          color: darkMode ? "#f1f5f9" : "#111",
        }}
      >
        <h2 style={{ textAlign: "center" }}>Register</h2>

        {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}

        {/* Username */}
        <input
          type="text"
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          style={styles.input(darkMode)}
          disabled={loading}
        />

        {/* Password */}
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

        {/* Confirm Password */}
        <div style={{ position: "relative", width: "100%" }}>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Confirm Password"
            value={form.confirmPassword}
            onChange={(e) =>
              setForm({ ...form, confirmPassword: e.target.value })
            }
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
          {loading ? "Registering..." : "Register"}{" "}
          {loading && <span style={styles.spinner}>⏳</span>}
        </button>

        <p style={{ textAlign: "center", fontSize: "14px" }}>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  );
}

const styles = {
  input: (darkMode) => ({
    width: "100%", // uniform width for all inputs
    padding: "10px 12px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    background: darkMode ? "#475569" : "#fff",
    color: darkMode ? "#f1f5f9" : "#111",
    fontSize: "14px",
    boxSizing: "border-box", // ensures padding doesn't break width
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
