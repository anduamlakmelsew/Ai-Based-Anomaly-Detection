import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../contexts/AuthProvider";
import { useNavigate, Link } from "react-router-dom";
import { login as authLogin } from "../../services/authService";

export default function EnhancedLogin() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Clear form on mount to prevent credential retention after logout
  useEffect(() => {
    setForm({ username: "", password: "" });
    setError("");
    setShowPassword(false);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.username || !form.password) {
      return setError("All fields are required");
    }

    try {
      setLoading(true);

      const result = await login(form.username, form.password);

      if (result.success) {
        setTimeout(() => navigate("/dashboard"), 100);
      } else {
        setError(result.error || "Login failed. Please try again.");
      }
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

  const containerStyle = {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "20px",
  };

  const cardStyle = {
    maxWidth: "420px",
    padding: "40px",
    borderRadius: "20px",
    background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
    color: "#f1f5f9",
    boxShadow: "0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.1)",
    border: "1px solid rgba(255,255,255,0.1)",
    backdropFilter: "blur(10px)",
  };

  const inputStyle = {
    width: "100%",
    padding: "12px 16px",
    borderRadius: "10px",
    border: "1px solid rgba(255,255,255,0.2)",
    background: "rgba(255,255,255,0.05)",
    color: "#f1f5f9",
    fontSize: "15px",
    transition: "all 0.3s ease",
    outline: "none"
  };

  const buttonStyle = {
    width: "100%",
    padding: "12px 24px",
    borderRadius: "10px",
    border: "none",
    background: loading ? "#374151" : "#3b82f6",
    color: "#fff",
    fontSize: "16px",
    fontWeight: "600",
    cursor: loading ? "not-allowed" : "pointer",
    transition: "all 0.3s ease",
  };

  const linkStyle = {
    color: "#94a3b8",
    textDecoration: "none",
    fontWeight: "500",
    transition: "color 0.3s ease",
  };

  return (
    <div style={containerStyle}>
      {/* Animated Background Elements */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{
          position: "absolute",
          width: "300px",
          height: "300px",
          background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
          borderRadius: "50%",
          filter: "blur(100px)",
          opacity: 0.3,
          top: "-100px",
          left: "-100px"
        }}
      />
      
      <motion.div
        animate={{
          scale: [1.2, 1, 1.2],
          rotate: [360, 180, 0],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{
          position: "absolute",
          width: "400px",
          height: "400px",
          background: "linear-gradient(135deg, #8b5cf6, #ec4899)",
          borderRadius: "50%",
          filter: "blur(120px)",
          opacity: 0.2,
          bottom: "-150px",
          right: "-150px"
        }}
      />

      <motion.form
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        onSubmit={handleLogin}
        style={cardStyle}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
          style={{ textAlign: "center", marginBottom: "30px" }}
        >
          <div style={{
            width: "60px",
            height: "60px",
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            borderRadius: "15px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 15px",
            fontSize: "24px"
          }}>
            🛡️
          </div>
          <h2 style={{ 
            margin: 0, 
            fontSize: "28px",
            fontWeight: "bold",
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}>
            Welcome Back
          </h2>
          <p style={{ 
            margin: "8px 0 0", 
            fontSize: "14px",
            color: "#94a3b8"
          }}>
            Sign in to access the security dashboard
          </p>
        </motion.div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              style={{
                padding: "12px",
                borderRadius: "8px",
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.3)",
                color: "#ef4444",
                marginBottom: "20px",
                fontSize: "14px"
              }}
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        <div style={{ marginBottom: "20px" }}>
          <label style={{ 
            display: "block", 
            marginBottom: "8px", 
            fontSize: "14px",
            fontWeight: "500",
            color: "#cbd5e1"
          }}>
            Username
          </label>
          <motion.input
            whileFocus={{ scale: 1.02 }}
            type="text"
            placeholder="Enter your username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            style={inputStyle}
            disabled={loading}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{ 
            display: "block", 
            marginBottom: "8px", 
            fontSize: "14px",
            fontWeight: "500",
            color: "#cbd5e1"
          }}>
            Password
          </label>
          <div style={{ position: "relative" }}>
            <motion.input
              whileFocus={{ scale: 1.02 }}
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              style={{ ...inputStyle, paddingRight: "45px" }}
              disabled={loading}
            />
            <motion.button
              type="button"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: "absolute",
                right: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: "18px",
                color: "#94a3b8"
              }}
            >
              {showPassword ? "🙈" : "👁"}
            </motion.button>
          </div>
        </div>

        <motion.button
          type="submit"
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          style={buttonStyle}
        >
          {loading ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              style={{ display: "inline-block" }}
            >
              ⏳
            </motion.div>
          ) : (
            "Sign In"
          )}
        </motion.button>

        {/* Demo Credentials */}
        <div style={{
          marginTop: "20px",
          padding: "12px",
          borderRadius: "8px",
          background: "rgba(59, 130, 246, 0.1)",
          border: "1px solid rgba(59, 130, 246, 0.3)",
        }}>
          <p style={{
            margin: "0 0 6px 0",
            fontSize: "12px",
            color: "#60a5fa",
            fontWeight: "600",
            textAlign: "center"
          }}>
            Demo Credentials
          </p>
          <p style={{
            margin: "0",
            fontSize: "13px",
            color: "#94a3b8",
            textAlign: "center"
          }}>
            Username: <span style={{ color: "#e2e8f0" }}>admin</span>
          </p>
          <p style={{
            margin: "4px 0 0 0",
            fontSize: "13px",
            color: "#94a3b8",
            textAlign: "center"
          }}>
            Password: <span style={{ color: "#e2e8f0" }}>admin123</span>
          </p>
        </div>

        <div style={{ 
          textAlign: "center", 
          marginTop: "20px",
          paddingTop: "20px",
          borderTop: "1px solid rgba(255,255,255,0.1)"
        }}>
          <p style={{ 
            margin: 0, 
            fontSize: "14px",
            color: "#94a3b8"
          }}>
            Don't have an account?{" "}
            <Link 
              to="/register" 
              style={{ 
                color: "#3b82f6", 
                textDecoration: "none",
                fontWeight: "500"
              }}
            >
              Sign up
            </Link>
          </p>
          <p style={{ margin: "10px 0 0", fontSize: "13px" }}>
            <Link 
              to="/forgot-password" 
              style={{ 
                color: "#94a3b8",
                textDecoration: "none"
              }}
            >
              Forgot your password?
            </Link>
          </p>
        </div>
      </motion.form>
    </div>
  );
}
