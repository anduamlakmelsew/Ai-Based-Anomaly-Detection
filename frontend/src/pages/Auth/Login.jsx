import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = () => {
    login();
    navigate("/dashboard");
  };

  return (
    <div style={{ padding: "40px" }}>
      <h2>Login - AI Baseline Assessment</h2>
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default Login;
