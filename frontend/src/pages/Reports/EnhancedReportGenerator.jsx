import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { getScanHistory, getScanById } from "../../services/scanService";
import { getToken } from "../../services/authService";
import { io } from "socket.io-client";

// Socket connection
// Socket connection with fallback
let socket = null;
let socketConnected = false;

try {
  socket = io("http://127.0.0.1:5003", {
    transports: ["websocket", "polling"],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 3
  });
  
  socket.on("connect", () => {
    console.log("✅ WebSocket connected");
    socketConnected = true;
  });
  
  socket.on("disconnect", () => {
    console.warn("⚠️ WebSocket disconnected");
    socketConnected = false;
  });
  
  socket.on("connect_error", (error) => {
    console.warn("⚠️ WebSocket connection failed, using HTTP polling fallback:", error.message);
    socketConnected = false;
  });
} catch (err) {
  console.warn("⚠️ WebSocket initialization failed, using HTTP polling fallback:", err);
  socket = null;
}

export default function EnhancedReportGenerator() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalReports: 0,
    criticalFindings: 0,
    highFindings: 0,
    mediumFindings: 0,
    avgRiskScore: 0
  });
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    loadReports();
    setupRealtimeUpdates();

    return () => {
      if (socket) socket.off("scan_completed");
      if (socket) socket.off("scan_progress");
    };
  }, []);

  const setupRealtimeUpdates = () => {
    if (!socket) return;

    // Listen for new scans to update reports
    socket.on("scan_completed", (data) => {
      console.log("New scan completed, refreshing reports:", data);
      loadReports();
    });

    // Listen for scan progress
    socket.on("scan_progress", (data) => {
      if (data.status === "completed") {
        loadReports();
      }
    });
  };

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await getScanHistory();
      const reportsData = Array.isArray(data) ? data : data?.data || [];
      setReports(reportsData);
      calculateStats(reportsData);
    } catch (err) {
      console.error("Failed to load reports:", err);
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (reportsData) => {
    let criticalCount = 0;
    let highCount = 0;
    let mediumCount = 0;
    let totalRisk = 0;
    let validRiskScores = 0;

    reportsData.forEach(report => {
      const findings = report.findings || [];
      findings.forEach(finding => {
        switch (finding.severity?.toUpperCase()) {
          case 'CRITICAL':
            criticalCount++;
            break;
          case 'HIGH':
            highCount++;
            break;
          case 'MEDIUM':
            mediumCount++;
            break;
        }
      });

      if (report.risk?.score && report.risk.score > 0) {
        totalRisk += report.risk.score;
        validRiskScores++;
      }
    });

    setStats({
      totalReports: reportsData.length,
      criticalFindings: criticalCount,
      highFindings: highCount,
      mediumFindings: mediumCount,
      avgRiskScore: validRiskScores > 0 ? Math.round(totalRisk / validRiskScores) : 0
    });
  };

  const loadReportDetails = async (report) => {
    try {
      setGenerating(true);
      const details = await getScanById(report.id || report.scan_id);
      setReportData(details?.data || details);
      setSelectedReport(report);
    } catch (err) {
      console.error("Failed to load report details:", err);
    } finally {
      setGenerating(false);
    }
  };

  const generateReport = (format = "json") => {
    if (!reportData) return;

    const reportContent = {
      metadata: {
        generated_at: new Date().toISOString(),
        scan_id: selectedReport?.id || selectedReport?.scan_id,
        target: selectedReport?.target,
        scan_type: selectedReport?.scan_type,
        format: format
      },
      summary: {
        total_findings: reportData.findings?.length || 0,
        risk_score: reportData.risk?.score || 0,
        risk_level: reportData.risk?.level || "LOW"
      },
      findings: reportData.findings || [],
      services: reportData.services || [],
      open_ports: reportData.open_ports || [],
      system_data: reportData.system_data || {},
      web_scan: reportData.web_scan || {}
    };

    if (format === "json") {
      downloadJSON(reportContent, `security_report_${selectedReport?.id || 'report'}.json`);
    } else if (format === "csv") {
      downloadCSV(reportContent, `security_report_${selectedReport?.id || 'report'}.csv`);
    }
  };

  const downloadJSON = (content, filename) => {
    const blob = new Blob([JSON.stringify(content, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadCSV = (content, filename) => {
    let csv = "Type,Severity,Category,Evidence,URL,Remediation\n";
    content.findings.forEach(finding => {
      csv += `"${finding.type || 'Unknown'}","${finding.severity || 'LOW'}","${finding.category || 'General'}","${finding.evidence || ''}","${finding.url || ''}","${finding.remediation || ''}"\n`;
    });
    
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getRiskColor = (level) => {
    switch ((level || '').toString().toUpperCase()) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MEDIUM': return '#eab308';
      case 'LOW': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const formatDate = (date) => {
    if (!date) return "-";
    return new Date(date).toLocaleString();
  };

  const cardStyle = {
    background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
    padding: "20px",
    borderRadius: "12px",
    border: "1px solid rgba(255,255,255,0.1)",
    color: "#fff",
    transition: "all 0.3s ease"
  };

  return (
    <div style={{ 
      color: "#fff", 
      padding: "20px",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
      minHeight: "100vh"
    }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 style={{ 
          fontSize: "28px", 
          marginBottom: "10px",
          background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent"
        }}>
          📊 Security Reports
        </h2>
        <p style={{ color: "#94a3b8", marginBottom: "30px" }}>
          Real-time security assessment reports and analytics
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "20px",
          marginBottom: "30px"
        }}
      >
        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>Total Reports</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#3b82f6" }}>
            {stats.totalReports}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Generated reports</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>Critical Findings</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#ef4444" }}>
            {stats.criticalFindings}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>High priority issues</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>High Findings</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#f97316" }}>
            {stats.highFindings}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Priority issues</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>Avg Risk Score</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: getRiskColor(stats.avgRiskScore) }}>
            {stats.avgRiskScore}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Overall risk level</p>
        </motion.div>
      </motion.div>

      {/* Reports Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={cardStyle}
      >
        <h3 style={{ marginBottom: "20px" }}>📜 Scan Reports</h3>
        
        {loading ? (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <div style={{ 
              width: "40px", 
              height: "40px", 
              border: "4px solid #334155", 
              borderTop: "4px solid #3b82f6",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              margin: "0 auto"
            }} />
            <p style={{ marginTop: "10px", color: "#94a3b8" }}>Loading reports...</p>
          </div>
        ) : reports.length === 0 ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>📊</div>
            <h3>No Reports Available</h3>
            <p>Start scanning to generate security reports</p>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
                  <th style={{ padding: "12px", textAlign: "left" }}>Date</th>
                  <th style={{ padding: "12px", textAlign: "left" }}>Type</th>
                  <th style={{ padding: "12px", textAlign: "left" }}>Target</th>
                  <th style={{ padding: "12px", textAlign: "left" }}>Risk</th>
                  <th style={{ padding: "12px", textAlign: "left" }}>Findings</th>
                  <th style={{ padding: "12px", textAlign: "left" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report, index) => (
                  <motion.tr
                    key={report.id || report.scan_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    style={{ 
                      borderBottom: "1px solid rgba(255,255,255,0.05)",
                      cursor: "pointer"
                    }}
                    whileHover={{ background: "rgba(255,255,255,0.05)" }}
                  >
                    <td style={{ padding: "12px" }}>
                      {formatDate(report.timestamp || report.date)}
                    </td>
                    <td style={{ padding: "12px" }}>
                      <span style={{
                        background: getScanTypeColor(report.scan_type),
                        padding: "4px 8px",
                        borderRadius: "4px",
                        fontSize: "12px",
                        fontWeight: "bold"
                      }}>
                        {report.scan_type?.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: "12px" }}>{report.target}</td>
                    <td style={{ padding: "12px" }}>
                      <span style={{
                        color: getRiskColor(report.risk?.level),
                        fontWeight: "bold"
                      }}>
                        {report.risk?.level || "LOW"}
                      </span>
                      <div style={{ fontSize: "11px", color: "#94a3b8" }}>
                        Score: {report.risk?.score || 0}
                      </div>
                    </td>
                    <td style={{ padding: "12px" }}>
                      {report.findings?.length || 0}
                    </td>
                    <td style={{ padding: "12px" }}>
                      <div style={{ display: "flex", gap: "8px" }}>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => loadReportDetails(report)}
                          disabled={generating}
                          style={{
                            padding: "4px 8px",
                            background: "#3b82f6",
                            color: "#fff",
                            border: "none",
                            borderRadius: "4px",
                            cursor: generating ? "not-allowed" : "pointer",
                            fontSize: "12px"
                          }}
                        >
                          {generating ? "Loading..." : "View"}
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => generateReport("json")}
                          style={{
                            padding: "4px 8px",
                            background: "#22c55e",
                            color: "#fff",
                            border: "none",
                            borderRadius: "4px",
                            cursor: "pointer",
                            fontSize: "12px"
                          }}
                        >
                          JSON
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => generateReport("csv")}
                          style={{
                            padding: "4px 8px",
                            background: "#f59e0b",
                            color: "#fff",
                            border: "none",
                            borderRadius: "4px",
                            cursor: "pointer",
                            fontSize: "12px"
                          }}
                        >
                          CSV
                        </motion.button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>

      {/* Report Details Modal */}
      {selectedReport && reportData && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}
          onClick={() => setSelectedReport(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            style={{
              background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
              padding: "30px",
              borderRadius: "16px",
              maxWidth: "800px",
              maxHeight: "80vh",
              overflowY: "auto",
              border: "1px solid rgba(255,255,255,0.1)"
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3>📊 Report Details</h3>
              <button
                onClick={() => setSelectedReport(null)}
                style={{
                  background: "none",
                  border: "none",
                  color: "#fff",
                  fontSize: "24px",
                  cursor: "pointer"
                }}
              >
                ×
              </button>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <p><strong>Target:</strong> {selectedReport.target}</p>
              <p><strong>Type:</strong> {selectedReport.scan_type?.toUpperCase()}</p>
              <p><strong>Date:</strong> {formatDate(selectedReport.timestamp)}</p>
              <p><strong>Risk Score:</strong> {reportData.risk?.score || 0} ({reportData.risk?.level || "LOW"})</p>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <h4>🚨 Findings Summary</h4>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))", gap: "10px" }}>
                {Object.entries(
                  (reportData.findings || []).reduce((acc, f) => {
                    const sev = f.severity || "LOW";
                    acc[sev] = (acc[sev] || 0) + 1;
                    return acc;
                  }, {})
                ).map(([severity, count]) => (
                  <div key={severity} style={{
                    background: getRiskColor(severity),
                    padding: "10px",
                    borderRadius: "8px",
                    textAlign: "center"
                  }}>
                    <div style={{ fontSize: "20px", fontWeight: "bold" }}>{count}</div>
                    <div style={{ fontSize: "12px" }}>{severity}</div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4>📋 Recent Findings</h4>
              <div style={{ maxHeight: "200px", overflowY: "auto" }}>
                {(reportData.findings || []).slice(0, 5).map((finding, index) => (
                  <div key={index} style={{
                    padding: "10px",
                    background: "rgba(255,255,255,0.05)",
                    borderRadius: "6px",
                    marginBottom: "8px",
                    borderLeft: `3px solid ${getRiskColor(finding.severity)}`
                  }}>
                    <div style={{ fontWeight: "bold" }}>{finding.type}</div>
                    <div style={{ fontSize: "12px", color: "#94a3b8" }}>{finding.evidence}</div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Back to Dashboard Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => navigate("/dashboard")}
        style={{
          padding: "12px 24px",
          background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
          color: "#fff",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
          fontSize: "14px",
          fontWeight: "500",
          marginTop: "20px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
        }}
      >
        🏠 Back to Dashboard
      </motion.button>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

function getScanTypeColor(type) {
  switch (type?.toLowerCase()) {
    case 'network': return '#3b82f6';
    case 'system': return '#8b5cf6';
    case 'web': return '#06b6d4';
    default: return '#6b7280';
  }
}
