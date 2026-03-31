import { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { getScanHistory } from "../../services/scanService";

import RiskScoreCard from "./RiskScoreCard";
import ActivityLog from "./ActivityLog";
import TrafficChart from "./TrafficChart";
import VulnerabilityPanel from "./VulnerabilityPanel";

// 🔴 Safe socket initialization
let socket;
try {
  socket = io("http://127.0.0.1:5000", {
    transports: ["websocket", "polling"],
  });
} catch (err) {
  console.warn("Socket failed:", err);
}

export default function Dashboard() {
  const [scans, setScans] = useState([]);
  const [liveScan, setLiveScan] = useState(null);

  useEffect(() => {
    loadData();

    if (socket) {
      socket.on("scan_progress", (data) => {
        setLiveScan(data);

        if (data.status === "completed") {
          loadData();
        }
      });
    }

    return () => {
      if (socket) socket.off("scan_progress");
    };
  }, []);

  const loadData = async () => {
    try {
      const data = await getScanHistory();
      setScans(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load scans:", err);
      setScans([]);
    }
  };

  // Process findings
  const allFindings = scans?.flatMap((s) => s.findings || []) || [];

  const severityCount = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
    INFO: 0,
  };

  let exploitableCount = 0;
  let totalUrls = 0;

  allFindings.forEach((f) => {
    const sev = f?.severity || "LOW";
    severityCount[sev] = (severityCount[sev] || 0) + 1;

    if (f?.exploits_available?.length > 0) exploitableCount++;
  });

  scans.forEach((s) => {
    totalUrls += s?.total_urls_scanned || 0;
  });

  const latestRisk = scans?.[0]?.risk || {
    score: 0,
    level: "LOW",
    explanation: "No data",
  };

  // ===== STYLING HELPERS =====
  const cardStyle = {
    background: "#1e293b",
    padding: "15px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
    color: "#fff",
  };

  const grid4 = {
    display: "grid",
    gridTemplateColumns: "repeat(4,1fr)",
    gap: "20px",
    marginTop: "20px",
  };

  const grid2 = {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "20px",
    marginTop: "20px",
  };

  return (
    <div className="dashboard" style={{ color: "#fff", paddingBottom: "50px" }}>
      <h2 style={{ marginBottom: "20px" }}>🛡️ Security Dashboard</h2>

      {/* LIVE SCAN */}
      {liveScan && liveScan.status !== "completed" && (
        <div style={{ ...cardStyle, marginBottom: "20px" }}>
          <h4>⚡ Live Scan</h4>
          <p>
            <strong>Stage:</strong> {liveScan.stage}
          </p>
          <p>
            <strong>Status:</strong> {liveScan.status}
          </p>

          <div
            style={{
              height: "12px",
              background: "#334155",
              borderRadius: "6px",
              overflow: "hidden",
              margin: "10px 0",
            }}
          >
            <div
              style={{
                width: `${liveScan.progress || 0}%`,
                height: "100%",
                background: "#22c55e",
                transition: "width 0.3s ease",
              }}
            />
          </div>
          <p>{liveScan.progress || 0}%</p>
        </div>
      )}

      {/* TOP CARDS */}
      <div style={grid4}>
        <RiskScoreCard risk={latestRisk} />

        <div style={cardStyle}>
          <h4>🚨 Critical</h4>
          <p style={{ fontSize: "24px", fontWeight: "bold" }}>
            {severityCount.CRITICAL}
          </p>
        </div>

        <div style={cardStyle}>
          <h4>⚠️ High</h4>
          <p style={{ fontSize: "24px", fontWeight: "bold" }}>
            {severityCount.HIGH}
          </p>
        </div>

        <div style={cardStyle}>
          <h4>💣 Exploitable</h4>
          <p style={{ fontSize: "24px", fontWeight: "bold" }}>
            {exploitableCount}
          </p>
        </div>
      </div>

      {/* SECOND ROW */}
      <div style={grid2}>
        <VulnerabilityPanel scans={scans} />

        <div style={cardStyle}>
          <h4>🌐 Coverage</h4>
          <p>Total URLs: {totalUrls}</p>
          <p>Total Findings: {allFindings.length}</p>
          <p>Risk: {latestRisk.level}</p>
        </div>
      </div>

      {/* TRAFFIC CHART */}
      <div style={{ marginTop: "20px" }}>
        <TrafficChart scans={scans} />
      </div>

      {/* ACTIVITY LOG */}
      <div style={{ marginTop: "20px" }}>
        <ActivityLog scans={scans} />
      </div>
    </div>
  );
}
