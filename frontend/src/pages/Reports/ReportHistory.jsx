import React, { useEffect, useState } from "react";
import { getScanHistory } from "../../services/scanService";

function ReportHistory() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const data = await getScanHistory();
      setReports(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load reports:", err);
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ color: "#fff" }}>
      <h2>📜 Report History</h2>

      {loading ? (
        <p>Loading reports...</p>
      ) : reports.length === 0 ? (
        <p>No reports available</p>
      ) : (
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "20px",
          }}
        >
          <thead>
            <tr>
              <th style={thStyle}>Target</th>
              <th style={thStyle}>Type</th>
              <th style={thStyle}>Risk</th>
              <th style={thStyle}>Findings</th>
              <th style={thStyle}>Date</th>
            </tr>
          </thead>

          <tbody>
            {reports.map((report) => (
              <tr key={report.id}>
                <td style={tdStyle}>{report.target}</td>
                <td style={tdStyle}>{report.scan_type}</td>

                <td style={tdStyle}>
                  <span style={getRiskStyle(report.risk?.level)}>
                    {report.risk?.level || "LOW"}
                  </span>
                </td>

                <td style={tdStyle}>{report.findings?.length || 0}</td>

                <td style={tdStyle}>{formatDate(report.date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// =========================
// 🎨 STYLES
// =========================
const thStyle = {
  textAlign: "left",
  padding: "10px",
  borderBottom: "1px solid #334155",
};

const tdStyle = {
  padding: "10px",
  borderBottom: "1px solid #1e293b",
};

// =========================
// 🎨 RISK COLORS (🔥 DEMO BOOST)
// =========================
const getRiskStyle = (level) => {
  switch (level) {
    case "CRITICAL":
      return { color: "#ef4444", fontWeight: "bold" };
    case "HIGH":
      return { color: "#f97316", fontWeight: "bold" };
    case "MEDIUM":
      return { color: "#eab308" };
    default:
      return { color: "#22c55e" };
  }
};

// =========================
// 🕒 DATE FORMATTER
// =========================
const formatDate = (date) => {
  if (!date) return "-";
  return new Date(date).toLocaleString();
};

export default ReportHistory;
