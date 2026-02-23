import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <div
      style={{
        width: "220px",
        height: "100vh",
        background: "#111827",
        color: "white",
        padding: "20px",
        position: "fixed",
      }}
    >
      <h3>AI Scanner</h3>
      <hr />

      <nav style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        <Link to="/dashboard" style={{ color: "white" }}>
          Dashboard
        </Link>
        <Link to="/baseline" style={{ color: "white" }}>
          Baseline
        </Link>
        <Link to="/scanner" style={{ color: "white" }}>
          Scanner
        </Link>
        <Link to="/anomalies" style={{ color: "white" }}>
          Anomalies
        </Link>
        <Link to="/alerts" style={{ color: "white" }}>
          Alerts
        </Link>
        <Link to="/reports" style={{ color: "white" }}>
          Reports
        </Link>
      </nav>
    </div>
  );
}

export default Sidebar;
