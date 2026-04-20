import { useState } from "react";
import { useAuth } from "../../contexts/AuthProvider";
import { useNavigate, Link } from "react-router-dom";
import { useTheme } from "../../context/ThemeContext";
import { login } from "../../services/authService";
import api from "../../services/api";

// Password validation utility
const validatePassword = (password) => {
  const errors = [];
  
  if (password.length < 8) {
    errors.push("At least 8 characters");
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push("One uppercase letter");
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push("One lowercase letter");
  }
  
  if (!/\d/.test(password)) {
    errors.push("One number");
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]/.test(password)) {
    errors.push("One special character");
  }
  
  // Check for common weak patterns
  const commonPatterns = ['123456', 'password', 'qwerty', 'admin', 'letmein', 'welcome'];
  if (commonPatterns.some(pattern => password.toLowerCase().includes(pattern))) {
    errors.push("Avoid common patterns");
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors,
    strength: calculateStrength(password)
  };
};

const calculateStrength = (password) => {
  let score = 0;
  
  if (password.length >= 8) score += 20;
  if (password.length >= 12) score += 10;
  if (/[a-z]/.test(password)) score += 10;
  if (/[A-Z]/.test(password)) score += 10;
  if (/\d/.test(password)) score += 10;
  if (/[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]/.test(password)) score += 10;
  
  const uniqueChars = new Set(password).size;
  if (uniqueChars >= password.length * 0.6) score += 15;
  else if (uniqueChars >= password.length * 0.4) score += 10;
  
  const commonPatterns = ['123456', 'password', 'qwerty', 'admin', 'letmein', 'welcome'];
  if (!commonPatterns.some(pattern => password.toLowerCase().includes(pattern))) score += 15;
  
  if (score >= 80) return "VERY_STRONG";
  if (score >= 60) return "STRONG";
  if (score >= 40) return "MEDIUM";
  if (score >= 20) return "WEAK";
  return "VERY_WEAK";
};

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { theme } = useTheme();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordValidation, setPasswordValidation] = useState({
    isValid: false,
    errors: [],
    strength: "VERY_WEAK"
  });
  const [suggestions, setSuggestions] = useState([]);

  const darkMode = theme === "dark";

  const handlePasswordChange = (password) => {
    setForm({ ...form, password });
    const validation = validatePassword(password);
    setPasswordValidation(validation);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.username || !form.email || !form.password || !form.confirmPassword) {
      return setError("All fields are required");
    }
    
    if (!passwordValidation.isValid) {
      return setError("Password does not meet security requirements: " + passwordValidation.errors.join(", "));
    }
    
    if (form.password !== form.confirmPassword) {
      return setError("Passwords do not match");
    }

    try {
      setLoading(true);
      console.log("📝 Submitting registration...");
      
      const response = await api.post("/auth/register", {
        username: form.username,
        email: form.email,
        password: form.password,
        role: "analyst"
      });

      const data = response.data;
      console.log("📨 Registration response:", data);

      if (data.success) {
        console.log("✅ Registration successful, attempting auto-login...");
        // Auto-login after successful registration
        const loginResult = await login(form.username, form.password);
        console.log("🔑 Login result:", loginResult);
        
        if (loginResult.success) {
          console.log("🚀 Navigating to dashboard...");
          // Update auth context with the registered user
          register(loginResult.user, loginResult.token);
          navigate("/dashboard", { replace: true });
        } else {
          setError("Registration successful but auto-login failed. Please try logging in manually.");
          setTimeout(() => navigate("/login"), 3000);
        }
      } else {
        if (data.errors && Array.isArray(data.errors)) {
          setError(data.errors.join(", "));
        } else {
          setError(data.message || data.error || "Registration failed. Please try again.");
          // Show suggestions if username is taken
          if (data.suggestions && data.suggestions.length > 0) {
            setSuggestions(data.suggestions);
          } else {
            setSuggestions([]);
          }
        }
      }
    } catch (err) {
      console.error("❌ Registration error:", err);
      const message = err.response?.data?.error || err.response?.data?.message || err.message || "Network error. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const getStrengthColor = (strength) => {
    switch (strength) {
      case "VERY_STRONG": return "#10b981";
      case "STRONG": return "#22c55e";
      case "MEDIUM": return "#f59e0b";
      case "WEAK": return "#ef4444";
      case "VERY_WEAK": return "#dc2626";
      default: return "#6b7280";
    }
  };

  const getStrengthText = (strength) => {
    switch (strength) {
      case "VERY_STRONG": return "Very Strong";
      case "STRONG": return "Strong";
      case "MEDIUM": return "Medium";
      case "WEAK": return "Weak";
      case "VERY_WEAK": return "Very Weak";
      default: return "";
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
          width: "400px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          padding: "24px",
          borderRadius: "12px",
          background: darkMode ? "#334155" : "#fff",
          color: darkMode ? "#f1f5f9" : "#111",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
        }}
      >
        <h2 style={{ textAlign: "center", marginBottom: "8px" }}>Register</h2>

        {error && (
          <div style={{
            padding: "12px",
            backgroundColor: "#fee2e2",
            color: "#dc2626",
            borderRadius: "6px",
            fontSize: "14px",
            textAlign: "center"
          }}>
            {error}
          </div>
        )}

        {/* Username */}
        <input
          type="text"
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          style={styles.input(darkMode)}
          disabled={loading}
        />

        {/* Email */}
        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          style={styles.input(darkMode)}
          disabled={loading}
        />

        {/* Password */}
        <div style={{ position: "relative", width: "100%" }}>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={form.password}
            onChange={(e) => handlePasswordChange(e.target.value)}
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

        {/* Password Strength Indicator */}
        {form.password && (
          <div style={{ fontSize: "12px" }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "4px"
            }}>
              <span>Password Strength:</span>
              <span style={{ 
                color: getStrengthColor(passwordValidation.strength),
                fontWeight: "bold"
              }}>
                {getStrengthText(passwordValidation.strength)}
              </span>
            </div>
            
            {/* Strength Bar */}
            <div style={{
              height: "4px",
              backgroundColor: darkMode ? "#475569" : "#e5e7eb",
              borderRadius: "2px",
              overflow: "hidden"
            }}>
              <div style={{
                height: "100%",
                width: `${(passwordValidation.strength === "VERY_WEAK" ? 20 : 
                          passwordValidation.strength === "WEAK" ? 40 :
                          passwordValidation.strength === "MEDIUM" ? 60 :
                          passwordValidation.strength === "STRONG" ? 80 : 100)}%`,
                backgroundColor: getStrengthColor(passwordValidation.strength),
                transition: "all 0.3s ease"
              }} />
            </div>

            {/* Password Requirements */}
            <div style={{ marginTop: "8px" }}>
              <div style={{ fontSize: "11px", marginBottom: "4px", opacity: 0.7 }}>
                Password must contain:
              </div>
              {[
                "At least 8 characters",
                "One uppercase letter",
                "One lowercase letter", 
                "One number",
                "One special character"
              ].map((requirement, index) => {
                const isMet = !passwordValidation.errors.includes(requirement.split(" ").slice(1).join(" "));
                return (
                  <div key={index} style={{
                    fontSize: "11px",
                    color: isMet ? "#10b981" : "#ef4444",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px"
                  }}>
                    <span>{isMet ? "✓" : "○"}</span>
                    <span>{requirement}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

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
          disabled={loading || !passwordValidation.isValid || form.password !== form.confirmPassword}
          style={{
            padding: "12px",
            backgroundColor: (!passwordValidation.isValid || form.password !== form.confirmPassword) 
              ? "#9ca3af" : "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: (!passwordValidation.isValid || form.password !== form.confirmPassword) 
              ? "not-allowed" : "pointer",
            fontSize: "16px",
            fontWeight: "500",
            transition: "background-color 0.2s",
          }}
        >
          {loading ? "Registering..." : "Register"}{" "}
          {loading && <span style={styles.spinner}>⏳</span>}
        </button>

        <p style={{ textAlign: "center", fontSize: "14px" }}>
          Already have an account? <Link to="/login" style={{ color: "#2563eb" }}>Login</Link>
        </p>
        
        {/* Username Suggestions */}
        {suggestions.length > 0 && (
          <div style={{ marginTop: "20px", padding: "15px", backgroundColor: darkMode ? "#1e293b" : "#f8fafc", borderRadius: "8px" }}>
            <p style={{ margin: "0 0 10px 0", fontSize: "14px", color: darkMode ? "#f1f5f9" : "#111827" }}>
              💡 Username suggestions:
            </p>
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                onClick={() => setForm({ ...form, username: suggestion })}
                style={{
                  display: "block",
                  width: "100%",
                  padding: "8px 12px",
                  margin: "5px 0",
                  backgroundColor: darkMode ? "#374151" : "#e5e7eb",
                  color: darkMode ? "#f1f5f9" : "#111827",
                  border: "1px solid #4b5563",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "14px",
                  textAlign: "left"
                }}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  );
}

const styles = {
  input: (darkMode) => ({
    width: "100%",
    padding: "12px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    background: darkMode ? "#475569" : "#fff",
    color: darkMode ? "#f1f5f9" : "#111",
    fontSize: "14px",
    boxSizing: "border-box",
  }),
  eye: {
    position: "absolute",
    right: "12px",
    top: "50%",
    transform: "translateY(-50%)",
    cursor: "pointer",
    fontSize: "16px",
    userSelect: "none",
  },
  spinner: {
    marginLeft: "8px",
    fontSize: "14px",
  },
};
