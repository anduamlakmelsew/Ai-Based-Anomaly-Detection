import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav
      className="card"
      style={{ display: "flex", justifyContent: "space-between" }}
    >
      <Link
        to="/dashboard"
        style={{ fontWeight: "bold", textDecoration: "none" }}
      >
        AI Scanner
      </Link>

      <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
        <button onClick={toggleTheme}>
          {theme === "dark" ? "☀ Light" : "🌙 Dark"}
        </button>

        {user && (
          <>
            <span>👤 {user.username}</span>
            <button onClick={handleLogout}>Logout</button>
          </>
        )}
      </div>
    </nav>
  );
}
