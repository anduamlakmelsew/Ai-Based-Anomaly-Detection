import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { getScanHistory } from "../../services/scanService";
import { getDashboardStats, getActivityFeed } from "../../services/dashboardService";
import { getToken, logout } from "../../services/authService";
import { io } from "socket.io-client";
import EnhancedRiskScoreCard from "./EnhancedRiskScoreCard";
import EnhancedActivityLog from "./EnhancedActivityLog";
import EnhancedTrafficChart from "./EnhancedTrafficChart";
import EnhancedVulnerabilityPanel from "./EnhancedVulnerabilityPanel";
import AIEventsPanel from "./AIEventsPanel";

// Helper functions
const getScanTypeColor = (type) => {
  switch (type?.toLowerCase()) {
    case 'network': return '#3b82f6';
    case 'system': return '#8b5cf6';
    case 'web': return '#06b6d4';
    default: return '#6b7280';
  }
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

const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Socket connection with fallback
let socket = null;

try {
  socket = io("http://127.0.0.1:5003", {
    transports: ["websocket", "polling"],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 3
  });
} catch (err) {
  console.warn("⚠️ WebSocket initialization failed:", err);
  socket = null;
}

export default function EnhancedDashboard() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [socketConnected, setSocketConnected] = useState(false);
  const [liveScan, setLiveScan] = useState(null);
  const navigate = useNavigate();
  const [selectedTimeRange, setSelectedTimeRange] = useState("all");
  const [animatedStats, setAnimatedStats] = useState({
    critical: 0,
    high: 0,
    exploitable: 0,
    totalScans: 0
  });

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    // Initial data load
    loadData();

    // Setup WebSocket listeners if available
    if (socket) {
      socket.on("connect", () => {
        console.log("✅ WebSocket connected");
        setSocketConnected(true);
      });
      
      socket.on("disconnect", () => {
        console.warn("⚠️ WebSocket disconnected");
        setSocketConnected(false);
      });
      
      socket.on("connect_error", (error) => {
        console.warn("⚠️ WebSocket connection failed:", error.message);
        setSocketConnected(false);
      });

      socket.on("scan_progress", (data) => {
        console.log("📡 Received scan_progress:", data);
        setLiveScan(data);

        if (data.status === "completed") {
          // Refresh data when scan completes
          setTimeout(() => loadData(), 500);
        }
      });

      // Listen for new scans to update dashboard
      socket.on("scan_completed", (data) => {
        console.log("✅ Scan completed, updating dashboard:", data);
        loadData();
      });
    } else {
      console.warn("⚠️ WebSocket not available - use manual refresh button");
    }

    return () => {
      if (socket) {
        socket.off("connect");
        socket.off("disconnect");
        socket.off("connect_error");
        socket.off("scan_progress");
        socket.off("scan_completed");
      }
    };
  }, []);

  useEffect(() => {
    // Animate stats when data changes
    const allFindings = scans?.flatMap((s) => s.findings || []) || [];
    const severityCount = {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
      INFO: 0,
    };

    let exploitableCount = 0;

    allFindings.forEach((f) => {
      const sev = f?.severity || "LOW";
      severityCount[sev] = (severityCount[sev] || 0) + 1;
      if (f?.exploits_available?.length > 0) exploitableCount++;
    });

    // Animate counter changes
    const duration = 1000;
    const steps = 20;
    const interval = duration / steps;

    let currentStep = 0;
    const startStats = { ...animatedStats };
    const endStats = {
      critical: severityCount.CRITICAL,
      high: severityCount.HIGH,
      exploitable: exploitableCount,
      totalScans: scans.length
    };

    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      
      setAnimatedStats({
        critical: Math.round(startStats.critical + (endStats.critical - startStats.critical) * progress),
        high: Math.round(startStats.high + (endStats.high - startStats.high) * progress),
        exploitable: Math.round(startStats.exploitable + (endStats.exploitable - startStats.exploitable) * progress),
        totalScans: Math.round(startStats.totalScans + (endStats.totalScans - startStats.totalScans) * progress)
      });

      if (currentStep >= steps) {
        clearInterval(timer);
      }
    }, interval);

    return () => clearInterval(timer);
  }, [scans]);

  const loadData = async () => {
    try {
      setLoading(true);
      console.log("📊 Loading dashboard data...");
      
      // Try dashboard stats API first for better aggregated data
      let dashboardData = null;
      try {
        const statsRes = await getDashboardStats();
        if (statsRes?.success && statsRes.data) {
          dashboardData = statsRes.data;
          console.log("✅ Dashboard stats loaded:", dashboardData);
        }
      } catch (statsErr) {
        console.warn("Dashboard stats API failed, falling back to scan history:", statsErr);
      }
      
      // Always load scan history for the list and charts
      const scanData = await getScanHistory();
      console.log(`✅ Loaded ${scanData.length} scans from history`);
      setScans(Array.isArray(scanData) ? scanData : []);
      
      // Log findings count for debugging
      const totalFindings = scanData.reduce((sum, s) => sum + (s.findings?.length || 0), 0);
      console.log(`📈 Total findings: ${totalFindings}`);
      
    } catch (err) {
      console.error("❌ Failed to load dashboard data:", err);
      setScans([]);
      if (err.response?.status !== 401) {
        console.error("Non-auth error:", err);
      }
    } finally {
      setLoading(false);
    }
  };

  const allFindings = scans?.flatMap((s) => s.findings || []) || [];
  const latestRisk = scans?.[0]?.risk || {
    score: 0,
    level: "LOW",
    explanation: "No data",
  };

  // Enhanced styling
  const cardStyle = {
    background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
    padding: "20px",
    borderRadius: "16px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1)",
    color: "#fff",
    border: "1px solid rgba(255,255,255,0.1)",
    backdropFilter: "blur(10px)",
    transition: "all 0.3s ease",
    cursor: "pointer"
  };

  const grid4 = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "20px",
    marginTop: "20px",
  };

  const grid2 = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
    gap: "20px",
    marginTop: "20px",
  };

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return '#ef4444';
      case 'high': return '#f97316';
      case 'medium': return '#eab308';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#0f172a'
      }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          style={{ 
            width: '60px', 
            height: '60px', 
            border: '4px solid #1e293b', 
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%'
          }}
        />
      </div>
    );
  }

  return (
    <div className="enhanced-dashboard" style={{ 
      color: "#fff", 
      paddingBottom: "50px",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
      minHeight: "100vh"
    }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h2 style={{ 
          marginBottom: "10px", 
          fontSize: "2.5rem",
          fontWeight: "bold",
          background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent"
        }}>
          🛡️ Security Command Center
        </h2>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <p style={{ color: "#94a3b8", margin: 0 }}>
              Real-time security monitoring and vulnerability assessment
            </p>
            {socketConnected && (
              <span style={{
                padding: "4px 8px",
                background: "#22c55e",
                color: "#fff",
                borderRadius: "4px",
                fontSize: "12px",
                fontWeight: "500"
              }}>
                🟢 Live
              </span>
            )}
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                console.log("🔄 Manual refresh triggered");
                loadData();
              }}
              style={{
                padding: "8px 16px",
                background: "linear-gradient(135deg, #3b82f6, #2563eb)",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "500",
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
              }}
            >
              🔄 Refresh
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                logout();
              }}
              style={{
                padding: "8px 16px",
                background: "linear-gradient(135deg, #ef4444, #dc2626)",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "500",
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
              }}
            >
              🚪 Logout
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Navigation Menu */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        style={{
          marginBottom: "30px",
          padding: "20px",
          background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
          borderRadius: "16px",
          border: "1px solid rgba(255,255,255,0.1)"
        }}
      >
        <h3 style={{ 
          marginBottom: "15px", 
          fontSize: "1.2rem",
          color: "#f1f5f9" 
        }}>
          🚀 Quick Navigation
        </h3>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "10px"
        }}>
          {[
            { name: "🔍 Scanner", path: "/scanner", color: "#3b82f6" },
            { name: "🚨 Alerts", path: "/alerts", color: "#ef4444" },
            { name: "🔍 Anomalies", path: "/anomalies", color: "#f97316" },
            { name: "📊 Reports", path: "/reports/generator", color: "#10b981" },
            { name: "⚙️ Settings", path: "/settings/user", color: "#6366f1" },
            { name: "📋 History", path: "/scanner/history", color: "#8b5cf6" }
          ].map((item, index) => (
            <motion.button
              key={item.name}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate(item.path)}
              style={{
                padding: "12px 16px",
                background: item.color,
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "500",
                transition: "all 0.3s ease",
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
              }}
            >
              {item.name}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Time Range Selector */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        style={{ marginBottom: "20px" }}
      >
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          {["all", "24h", "7d", "30d"].map((range) => (
            <button
              key={range}
              onClick={() => setSelectedTimeRange(range)}
              style={{
                padding: "8px 16px",
                borderRadius: "8px",
                border: "1px solid rgba(255,255,255,0.2)",
                background: selectedTimeRange === range ? "#3b82f6" : "transparent",
                color: "#fff",
                cursor: "pointer",
                transition: "all 0.3s ease"
              }}
            >
              {range === "all" ? "All Time" : 
               range === "24h" ? "Last 24h" :
               range === "7d" ? "Last 7 days" : "Last 30 days"}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Live Scan Banner */}
      <AnimatePresence>
        {liveScan && liveScan.status !== "completed" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            style={{ 
              ...cardStyle, 
              marginBottom: "20px",
              background: "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
              border: "1px solid rgba(59, 130, 246, 0.5)"
            }}
          >
            <h4 style={{ marginBottom: "15px" }}>⚡ Live Scan in Progress</h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
              <div>
                <p><strong>Target:</strong> {liveScan.target}</p>
                <p><strong>Type:</strong> {liveScan.scan_type}</p>
              </div>
              <div>
                <p><strong>Stage:</strong> {liveScan.stage}</p>
                <p><strong>Status:</strong> {liveScan.status}</p>
              </div>
            </div>
            
            <div style={{ marginTop: "15px" }}>
              <div style={{ 
                display: "flex", 
                justifyContent: "space-between", 
                marginBottom: "5px" 
              }}>
                <span>Progress</span>
                <span>{liveScan.progress || 0}%</span>
              </div>
              <div
                style={{
                  height: "8px",
                  background: "rgba(255,255,255,0.2)",
                  borderRadius: "4px",
                  overflow: "hidden",
                }}
              >
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${liveScan.progress || 0}%` }}
                  transition={{ duration: 0.5 }}
                  style={{
                    height: "100%",
                    background: "linear-gradient(90deg, #22c55e, #10b981)",
                    borderRadius: "4px",
                  }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Top Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={grid4}
      >
        <motion.div
          whileHover={{ scale: 1.05, y: -5 }}
          style={cardStyle}
        >
          <EnhancedRiskScoreCard risk={latestRisk} />
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05, y: -5 }}
          style={{ 
            ...cardStyle, 
            borderLeft: `4px solid #ef4444`,
            background: "linear-gradient(135deg, #1e293b 0%, #991b1b 100%)"
          }}
        >
          <h4 style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            🚨 Critical
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{ 
                background: "#ef4444", 
                color: "#fff", 
                padding: "2px 8px", 
                borderRadius: "12px", 
                fontSize: "12px" 
              }}
            >
              LIVE
            </motion.span>
          </h4>
          <motion.p 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
            style={{ 
              fontSize: "32px", 
              fontWeight: "bold", 
              margin: "10px 0",
              color: "#ef4444"
            }}
          >
            {animatedStats.critical}
          </motion.p>
          <p style={{ fontSize: "14px", color: "#94a3b8" }}>
            Immediate attention required
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05, y: -5 }}
          style={{ 
            ...cardStyle, 
            borderLeft: `4px solid #f97316`,
            background: "linear-gradient(135deg, #1e293b 0%, #c2410c 100%)"
          }}
        >
          <h4>⚠️ High Risk</h4>
          <motion.p 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
            style={{ 
              fontSize: "32px", 
              fontWeight: "bold", 
              margin: "10px 0",
              color: "#f97316"
            }}
          >
            {animatedStats.high}
          </motion.p>
          <p style={{ fontSize: "14px", color: "#94a3b8" }}>
            Priority issues detected
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05, y: -5 }}
          style={{ 
            ...cardStyle, 
            borderLeft: `4px solid #dc2626`,
            background: "linear-gradient(135deg, #1e293b 0%, #991b1b 100%)"
          }}
        >
          <h4>💣 Exploitable</h4>
          <motion.p 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
            style={{ 
              fontSize: "32px", 
              fontWeight: "bold", 
              margin: "10px 0",
              color: "#dc2626"
            }}
          >
            {animatedStats.exploitable}
          </motion.p>
          <p style={{ fontSize: "14px", color: "#94a3b8" }}>
            Known exploits available
          </p>
        </motion.div>
      </motion.div>

      {/* Second Row */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        style={grid2}
      >
        <motion.div
          whileHover={{ scale: 1.02 }}
          style={cardStyle}
        >
          <EnhancedVulnerabilityPanel scans={scans} />
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          style={cardStyle}
        >
          <h4>📊 Scan Overview</h4>
          <div style={{ marginTop: "15px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
              <span>Total Scans</span>
              <span style={{ fontWeight: "bold" }}>{animatedStats.totalScans}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
              <span>Total Findings</span>
              <span style={{ fontWeight: "bold" }}>{allFindings.length}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
              <span>Current Risk</span>
              <span 
                style={{ 
                  fontWeight: "bold", 
                  color: getRiskColor(latestRisk.level)
                }}
              >
                {latestRisk.level}
              </span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span>Risk Score</span>
              <span style={{ fontWeight: "bold" }}>{latestRisk.score}/100</span>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* AI Events Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        style={{ marginTop: "20px" }}
      >
        <AIEventsPanel />
      </motion.div>

      {/* Traffic Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        style={{ marginTop: "20px" }}
      >
        <motion.div
          whileHover={{ scale: 1.01 }}
          style={cardStyle}
        >
          <EnhancedTrafficChart scans={scans} />
        </motion.div>
      </motion.div>

      {/* ACTIVITY LOG */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        style={{ marginTop: "20px" }}
      >
        <motion.div
          whileHover={{ scale: 1.01 }}
          style={cardStyle}
        >
          <EnhancedActivityLog scans={scans} />
        </motion.div>
      </motion.div>

      {/* RECENT SCAN RESULTS */}
      {scans.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          style={{ marginTop: "20px" }}
        >
          <motion.div
            whileHover={{ scale: 1.01 }}
            style={cardStyle}
          >
            <h3 style={{ marginBottom: "20px" }}>🔍 Recent Scan Results</h3>
            <div style={{ maxHeight: "400px", overflowY: "auto" }}>
              {scans.slice(0, 5).map((scan, index) => (
                <motion.div
                  key={scan.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  style={{
                    padding: "15px",
                    marginBottom: "12px",
                    borderRadius: "8px",
                    background: "rgba(255,255,255,0.05)",
                    border: `1px solid ${getRiskColor(scan.risk?.level)}40`,
                    borderLeft: `4px solid ${getRiskColor(scan.risk?.level)}`
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                        <span style={{
                          background: getScanTypeColor(scan.scan_type),
                          padding: "4px 8px",
                          borderRadius: "4px",
                          fontSize: "12px",
                          fontWeight: "bold"
                        }}>
                          {scan.scan_type?.toUpperCase()}
                        </span>
                        <span style={{
                          background: getRiskColor(scan.risk?.level),
                          color: "#fff",
                          padding: "2px 6px",
                          borderRadius: "12px",
                          fontSize: "10px"
                        }}>
                          {scan.risk?.level || "LOW"}
                        </span>
                      </div>
                      
                      <p style={{ margin: "0 0 8px 0", fontSize: "14px", color: "#fff" }}>
                        🎯 {scan.target}
                      </p>
                      
                      <div style={{ display: "flex", gap: "15px", fontSize: "12px", color: "#94a3b8" }}>
                        <span>📊 Score: {scan.risk?.score || 0}</span>
                        <span>🔍 Findings: {scan.findings?.length || 0}</span>
                        <span>📅 {formatDate(scan.timestamp)}</span>
                      </div>
                    </div>
                    
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "24px", fontWeight: "bold", color: getRiskColor(scan.risk?.level) }}>
                        {scan.findings?.length || 0}
                      </div>
                      <div style={{ fontSize: "10px", color: "#94a3b8" }}>Findings</div>
                    </div>
                  </div>
                  
                  {/* Show top findings */}
                  {scan.findings && scan.findings.length > 0 && (
                    <div style={{ marginTop: "10px", paddingTop: "10px", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
                      <div style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "5px" }}>Top Issues:</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
                        {scan.findings.slice(0, 3).map((finding, i) => (
                          <span key={i} style={{
                            background: "rgba(255,255,255,0.1)",
                            padding: "2px 6px",
                            borderRadius: "4px",
                            fontSize: "10px",
                            color: getSeverityColor(finding.severity)
                          }}>
                            {finding.type}
                          </span>
                        ))}
                        {scan.findings.length > 3 && (
                          <span style={{
                            background: "rgba(255,255,255,0.1)",
                            padding: "2px 6px",
                            borderRadius: "4px",
                            fontSize: "10px",
                            color: "#94a3b8"
                          }}>
                            +{scan.findings.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )} 
    </div>
  );
}
