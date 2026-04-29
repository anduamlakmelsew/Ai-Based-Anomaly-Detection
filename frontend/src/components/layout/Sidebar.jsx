import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();
  const [openSections, setOpenSections] = useState({
    scanner: true,
    alerts: true,
    anomalies: true,
    baseline: true,
    reports: true,
    settings: true,
  });

  const toggleSection = (section) => {
    setOpenSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const isActive = (path) => location.pathname === path;

  const linkStyle = (path) => ({
    display: "block",
    padding: "5px 0",
    color: isActive(path) ? "#2563eb" : "white",
    textDecoration: "none",
  });

  return (
    <div
      style={{
        width: "220px",
        background: "#020617",
        height: "100vh",
        padding: "20px",
        color: "white",
        overflowY: "auto",
      }}
    >
      <h3 style={{ marginBottom: "20px" }}>AI Baseline Scanner</h3>

      {/* Dashboard */}
      <Link to="/dashboard" style={linkStyle("/dashboard")}>
        Dashboard
      </Link>

      {/* AI Security Lab */}
      <Link to="/ai-lab" style={linkStyle("/ai-lab")}>
        🧪 AI Security Lab
      </Link>

      {/* Scanner */}
      <div style={{ marginTop: "15px" }}>
        <div
          onClick={() => toggleSection("scanner")}
          style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "5px" }}
        >
          Scanner {openSections.scanner ? "▾" : "▸"}
        </div>
        {openSections.scanner && (
          <div style={{ paddingLeft: "15px" }}>
            <Link to="/scanner" style={linkStyle("/scanner")}>
              Scanner Home
            </Link>
            <Link to="/scanner/form" style={linkStyle("/scanner/form")}>
              Start Scan
            </Link>
            <Link to="/scanner/history" style={linkStyle("/scanner/history")}>
              Scan History
            </Link>
          </div>
        )}
      </div>

      {/* Alerts */}
      <div style={{ marginTop: "15px" }}>
        <div
          onClick={() => toggleSection("alerts")}
          style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "5px" }}
        >
          Alerts {openSections.alerts ? "▾" : "▸"}
        </div>
        {openSections.alerts && (
          <div style={{ paddingLeft: "15px" }}>
            <Link to="/alerts" style={linkStyle("/alerts")}>
              Alert List
            </Link>
          </div>
        )}
      </div>

      {/* Anomalies */}
      <div style={{ marginTop: "15px" }}>
        <div
          onClick={() => toggleSection("anomalies")}
          style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "5px" }}
        >
          Anomalies {openSections.anomalies ? "▾" : "▸"}
        </div>
        {openSections.anomalies && (
          <div style={{ paddingLeft: "15px" }}>
            <Link to="/anomalies" style={linkStyle("/anomalies")}>
              Dashboard
            </Link>
            <Link
              to="/anomalies/model-performance"
              style={linkStyle("/anomalies/model-performance")}
            >
              Model Performance
            </Link>
            <Link
              to="/anomalies/traffic-graph"
              style={linkStyle("/anomalies/traffic-graph")}
            >
              Traffic Graph
            </Link>
          </div>
        )}
      </div>

      {/* Baseline */}
      <div style={{ marginTop: "15px" }}>
        <div
          onClick={() => toggleSection("baseline")}
          style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "5px" }}
        >
          Baseline {openSections.baseline ? "▾" : "▸"}
        </div>
        {openSections.baseline && (
          <div style={{ paddingLeft: "15px" }}>
            <Link
              to="/baseline/overview"
              style={linkStyle("/baseline/overview")}
            >
              Overview
            </Link>
            <Link
              to="/baseline/versioning"
              style={linkStyle("/baseline/versioning")}
            >
              Versioning
            </Link>
            <Link
              to="/baseline/compliance"
              style={linkStyle("/baseline/compliance")}
            >
              Compliance
            </Link>
          </div>
        )}
      </div>

      {/* Reports */}
      <div style={{ marginTop: "15px" }}>
        <div
          onClick={() => toggleSection("reports")}
          style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "5px" }}
        >
          Reports {openSections.reports ? "▾" : "▸"}
        </div>
        {openSections.reports && (
          <div style={{ paddingLeft: "15px" }}>
            <Link
              to="/reports/generator"
              style={linkStyle("/reports/generator")}
            >
              Generate Report
            </Link>
            <Link to="/reports/history" style={linkStyle("/reports/history")}>
              Report History
            </Link>
          </div>
        )}
      </div>

      {/* Settings */}
      <div style={{ marginTop: "15px" }}>
        <div
          onClick={() => toggleSection("settings")}
          style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "5px" }}
        >
          Settings {openSections.settings ? "▾" : "▸"}
        </div>
        {openSections.settings && (
          <div style={{ paddingLeft: "15px" }}>
            <Link to="/settings/admin" style={linkStyle("/settings/admin")}>
              Admin
            </Link>
            <Link
              to="/settings/notifications"
              style={linkStyle("/settings/notifications")}
            >
              Notifications
            </Link>
            <Link
              to="/settings/security"
              style={linkStyle("/settings/security")}
            >
              Security
            </Link>
            <Link to="/settings/user" style={linkStyle("/settings/user")}>
              User Settings
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
