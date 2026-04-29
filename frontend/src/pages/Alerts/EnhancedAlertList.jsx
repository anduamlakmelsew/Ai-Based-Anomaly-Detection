import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import { motion, AnimatePresence } from "framer-motion";
import { getScanHistory } from "../../services/scanService";
import { getToken } from "../../services/authService";

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

export default function EnhancedAlertList() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [stats, setStats] = useState({
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    total: 0
  });

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    loadAlerts();
    setupRealtimeUpdates();

    return () => {
      if (socket) socket.off("scan_completed");
      if (socket) socket.off("new_alert");
    };
  }, []);

  const setupRealtimeUpdates = () => {
    if (!socket) return;

    // Listen for new scans to generate alerts
    socket.on("scan_completed", (data) => {
      console.log("New scan completed, generating alerts:", data);
      generateAlertsFromScan(data);
    });

    // Listen for new alerts
    socket.on("new_alert", (alert) => {
      setAlerts(prev => [alert, ...prev].slice(0, 100)); // Keep latest 100
      updateStats([alert, ...alerts]);
    });

    // Listen for scan progress for real-time alerts
    socket.on("scan_progress", (data) => {
      if (data.status === "completed") {
        generateAlertsFromScan(data);
      }
    });
  };

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await getScanHistory();
      const scans = Array.isArray(data) ? data : data?.data || [];
      
      // Generate alerts from scan history
      const generatedAlerts = [];
      scans.forEach(scan => {
        const alerts = generateAlertsFromScan(scan, false);
        generatedAlerts.push(...alerts);
      });
      
      setAlerts(generatedAlerts);
      updateStats(generatedAlerts);
    } catch (err) {
      console.error("Failed to load alerts:", err);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  const generateAlertsFromScan = (scan, addToState = true) => {
    if (!scan || !scan.findings) return [];

    const newAlerts = [];
    const scanFindings = Array.isArray(scan.findings) ? scan.findings : [];
    
    scanFindings.forEach((finding, index) => {
      const alert = {
        id: `alert_${scan.id || scan.scan_id}_${index}`,
        scan_id: scan.id || scan.scan_id,
        title: generateAlertTitle(finding),
        description: finding.evidence || finding.description || "Security finding detected",
        severity: finding.severity || "LOW",
        category: finding.category || "General",
        target: scan.target,
        scan_type: scan.scan_type,
        timestamp: scan.timestamp || new Date().toISOString(),
        status: "active",
        acknowledged: false,
        finding: finding
      };
      
      newAlerts.push(alert);
    });

    if (addToState) {
      setAlerts(prev => [...newAlerts, ...prev].slice(0, 100));
      updateStats([...newAlerts, ...alerts]);
    }

    return newAlerts;
  };

  const generateAlertTitle = (finding) => {
    const type = finding.type || "Security Issue";
    const severity = finding.severity || "LOW";
    return `${severity}: ${type}`;
  };

  const updateStats = (alertsList) => {
    const stats = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      total: alertsList.length
    };

    alertsList.forEach(alert => {
      switch (alert.severity?.toUpperCase()) {
        case 'CRITICAL':
          stats.critical++;
          break;
        case 'HIGH':
          stats.high++;
          break;
        case 'MEDIUM':
          stats.medium++;
          break;
        case 'LOW':
          stats.low++;
          break;
      }
    });

    setStats(stats);
  };

  const acknowledgeAlert = (alertId) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true, status: "acknowledged" } : alert
    ));
    updateStats(alerts.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ));
  };

  const dismissAlert = (alertId) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, status: "dismissed" } : alert
    ));
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MEDIUM': return '#eab308';
      case 'LOW': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return '🚨';
      case 'HIGH': return '⚠️';
      case 'MEDIUM': return '⚡';
      case 'LOW': return 'ℹ️';
      default: return '📋';
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filter === "all") return true;
    if (filter === "active") return alert.status === "active";
    if (filter === "acknowledged") return alert.acknowledged;
    return alert.severity?.toLowerCase() === filter;
  });

  const formatDate = (date) => {
    if (!date) return "-";
    const now = new Date();
    const alertDate = new Date(date);
    const diff = now - alertDate;
    
    if (diff < 60000) return "Just now";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return alertDate.toLocaleDateString();
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
          background: "linear-gradient(135deg, #ef4444, #f97316)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent"
        }}>
          🚨 Security Alerts
        </h2>
        <p style={{ color: "#94a3b8", marginBottom: "30px" }}>
          Real-time security alerts and threat monitoring
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "20px",
          marginBottom: "30px"
        }}
      >
        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>{getSeverityIcon('CRITICAL')} Critical</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#ef4444" }}>
            {stats.critical}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Immediate action</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>{getSeverityIcon('HIGH')} High</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#f97316" }}>
            {stats.high}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Priority issues</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>{getSeverityIcon('MEDIUM')} Medium</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#eab308" }}>
            {stats.medium}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Monitor closely</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>{getSeverityIcon('LOW')} Low</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#22c55e" }}>
            {stats.low}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Minor issues</p>
        </motion.div>
      </motion.div>

      {/* Filter Tabs */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        style={{ display: "flex", gap: "10px", marginBottom: "20px" }}
      >
        {["all", "critical", "high", "medium", "low", "active", "acknowledged"].map((filterOption) => (
          <button
            key={filterOption}
            onClick={() => setFilter(filterOption)}
            style={{
              padding: "8px 16px",
              borderRadius: "8px",
              border: "1px solid rgba(255,255,255,0.2)",
              background: filter === filterOption ? "#3b82f6" : "transparent",
              color: "#fff",
              cursor: "pointer",
              transition: "all 0.3s ease",
              fontWeight: filter === filterOption ? "bold" : "normal",
              textTransform: "capitalize"
            }}
          >
            {filterOption === "all" && "All"}
            {filterOption === "critical" && "🚨 Critical"}
            {filterOption === "high" && "⚠️ High"}
            {filterOption === "medium" && "⚡ Medium"}
            {filterOption === "low" && "ℹ️ Low"}
            {filterOption === "active" && "🔴 Active"}
            {filterOption === "acknowledged" && "✅ Acknowledged"}
          </button>
        ))}
      </motion.div>

      {/* Alerts List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        style={cardStyle}
      >
        <h3 style={{ marginBottom: "20px" }}>📋 Alert Feed</h3>
        
        {loading ? (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <div style={{ 
              width: "40px", 
              height: "40px", 
              border: "4px solid #334155", 
              borderTop: "4px solid #ef4444",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              margin: "0 auto"
            }} />
            <p style={{ marginTop: "10px", color: "#94a3b8" }}>Loading alerts...</p>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>🛡️</div>
            <h3>No Alerts</h3>
            <p>Great! No security alerts detected</p>
          </div>
        ) : (
          <div style={{ maxHeight: "600px", overflowY: "auto" }}>
            <AnimatePresence>
              {filteredAlerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.05 }}
                  style={{
                    padding: "15px",
                    marginBottom: "12px",
                    borderRadius: "8px",
                    background: alert.acknowledged 
                      ? "rgba(34, 197, 94, 0.1)" 
                      : "rgba(255,255,255,0.05)",
                    border: `1px solid ${getSeverityColor(alert.severity)}40`,
                    borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
                    cursor: "pointer"
                  }}
                  whileHover={{ scale: 1.02, background: "rgba(255,255,255,0.08)" }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                        <span style={{ fontSize: "18px" }}>
                          {getSeverityIcon(alert.severity)}
                        </span>
                        <h4 style={{ margin: 0, fontSize: "16px" }}>
                          {alert.title}
                        </h4>
                        {alert.acknowledged && (
                          <span style={{
                            background: "#22c55e",
                            color: "#fff",
                            padding: "2px 6px",
                            borderRadius: "4px",
                            fontSize: "10px"
                          }}>
                            Acknowledged
                          </span>
                        )}
                      </div>
                      
                      <p style={{ 
                        margin: "0 0 8px 0", 
                        fontSize: "14px", 
                        color: "#94a3b8",
                        lineHeight: 1.4
                      }}>
                        {alert.description}
                      </p>
                      
                      <div style={{ display: "flex", gap: "15px", fontSize: "12px", color: "#94a3b8" }}>
                        <span>🎯 {alert.target}</span>
                        <span>🔍 {alert.scan_type?.toUpperCase()}</span>
                        <span>📅 {formatDate(alert.timestamp)}</span>
                      </div>
                    </div>
                    
                    <div style={{ display: "flex", gap: "8px", marginLeft: "15px" }}>
                      {!alert.acknowledged && (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => acknowledgeAlert(alert.id)}
                          style={{
                            padding: "6px 12px",
                            background: "#22c55e",
                            color: "#fff",
                            border: "none",
                            borderRadius: "6px",
                            cursor: "pointer",
                            fontSize: "12px"
                          }}
                        >
                          Acknowledge
                        </motion.button>
                      )}
                      
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => dismissAlert(alert.id)}
                        style={{
                          padding: "6px 12px",
                          background: "#ef4444",
                          color: "#fff",
                          border: "none",
                          borderRadius: "6px",
                          cursor: "pointer",
                          fontSize: "12px"
                        }}
                      >
                        Dismiss
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </motion.div>

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
