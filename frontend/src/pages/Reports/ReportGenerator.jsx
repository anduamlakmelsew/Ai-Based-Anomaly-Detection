// src/pages/Reports/ReportGenerator.jsx

import { useEffect, useState } from "react";
import Table from "../../components/common/Table";
import { getScanHistory } from "../../services/scanService";

function ReportGenerator() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const data = await getScanHistory();

      // Normalize: backend may return { success, data: [...] } or plain array
      const reports = Array.isArray(data) ? data : data?.data || [];
      setReports(reports);
    } catch (err) {
      console.error("Failed to load reports:", err);
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // 📥 DOWNLOAD REPORT (🔥 DEMO FEATURE)
  // =========================
  const downloadReport = (report) => {
    const content = JSON.stringify(report, null, 2);

    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `scan_report_${report.id}.json`;
    a.click();

    URL.revokeObjectURL(url);
  };

  // =========================
  // 📊 TABLE CONFIG
  // =========================
  const columns = ["Date", "Type", "Target", "Risk", "Findings", "Action"];

  const tableData = reports.map((report) => ({
    Date: formatDate(report.date),
    Type: report.scan_type,
    Target: report.target,

    Risk: (
      <span style={getRiskStyle(report.risk?.level)}>
        {report.risk?.level || "LOW"}
      </span>
    ),

    Findings: report.findings?.length || 0,

    Action: (
      <button onClick={() => downloadReport(report)} style={downloadBtn}>
        Download
      </button>
    ),
  }));

  // =========================
  // 📊 SUMMARY
  // =========================
  const totalReports = reports.length;

  const lastGenerated = reports[0]?.date ? formatDate(reports[0].date) : "-";

  return (
    <div style={{ padding: "20px", color: "#fff" }}>
      <h2>📊 Reports Module</h2>

      {loading ? (
        <p>Loading reports...</p>
      ) : (
        <>
          {/* SUMMARY CARDS */}
          <div style={cardContainer}>
            <div style={{ ...cardStyle, backgroundColor: "#2563eb" }}>
              <h3>Total Reports</h3>
              <p style={cardNumber}>{totalReports}</p>
            </div>

            <div style={{ ...cardStyle, backgroundColor: "#16a34a" }}>
              <h3>Last Generated</h3>
              <p style={cardNumber}>{lastGenerated}</p>
            </div>
          </div>

          {/* TABLE */}
          <div style={{ marginTop: "40px" }}>
            <h3>📜 Generated Reports</h3>
            {reports.length === 0 ? (
              <p>No reports available</p>
            ) : (
              <Table columns={columns} data={tableData} />
            )}
          </div>
        </>
      )}
    </div>
  );
}

// =========================
// 🎨 STYLES
// =========================
const cardContainer = {
  display: "flex",
  gap: "20px",
  marginTop: "20px",
  flexWrap: "wrap",
};

const cardStyle = {
  color: "white",
  padding: "20px",
  borderRadius: "10px",
  minWidth: "150px",
  textAlign: "center",
};

const cardNumber = {
  fontSize: "24px",
  margin: "10px 0",
};

const downloadBtn = {
  padding: "5px 10px",
  backgroundColor: "#16a34a",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
};

// =========================
// 🎨 RISK COLORS
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

export default ReportGenerator;
