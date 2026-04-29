import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import { motion } from "framer-motion";
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

export default function EnhancedAnomalyDashboard() {
  const navigate = useNavigate();
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [timeRange, setTimeRange] = useState("24h");
  const [stats, setStats] = useState({
    totalAnomalies: 0,
    criticalAnomalies: 0,
    highAnomalies: 0,
    mediumAnomalies: 0,
    lowAnomalies: 0,
    trend: "stable"
  });

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    loadAnomalies();
    setupRealtimeUpdates();

    return () => {
      if (socket) socket.off("scan_completed");
      if (socket) socket.off("anomaly_detected");
    };
  }, []);

  const setupRealtimeUpdates = () => {
    if (!socket) return;

    // Listen for new scans to detect anomalies
    socket.on("scan_completed", (data) => {
      console.log("New scan completed, analyzing for anomalies:", data);
      analyzeScanForAnomalies(data);
    });

    // Listen for anomaly detections
    socket.on("anomaly_detected", (anomaly) => {
      setAnomalies(prev => [anomaly, ...prev].slice(0, 100));
      updateStats([anomaly, ...anomalies]);
    });

    // Listen for scan progress
    socket.on("scan_progress", (data) => {
      if (data.status === "completed") {
        analyzeScanForAnomalies(data);
      }
    });
  };

  const loadAnomalies = async () => {
    try {
      setLoading(true);
      const data = await getScanHistory();
      const scans = Array.isArray(data) ? data : data?.data || [];
      
      // Analyze scan history for anomalies
      const detectedAnomalies = [];
      scans.forEach(scan => {
        const anomalies = analyzeScanForAnomalies(scan, false);
        detectedAnomalies.push(...anomalies);
      });
      
      setAnomalies(detectedAnomalies);
      updateStats(detectedAnomalies);
    } catch (err) {
      console.error("Failed to load anomalies:", err);
      setAnomalies([]);
    } finally {
      setLoading(false);
    }
  };

  const analyzeScanForAnomalies = (scan, addToState = true) => {
    if (!scan || !scan.findings) return [];

    const detectedAnomalies = [];
    const scanFindings = Array.isArray(scan.findings) ? scan.findings : [];
    
    // Detect various types of anomalies
    detectedAnomalies.push(...detectSeverityAnomalies(scan, scanFindings));
    detectedAnomalies.push(...detectPatternAnomalies(scan, scanFindings));
    detectedAnomalies.push(...detectTemporalAnomalies(scan, scanFindings));
    detectedAnomalies.push(...detectServiceAnomalies(scan, scanFindings));

    if (addToState) {
      setAnomalies(prev => [...detectedAnomalies, ...prev].slice(0, 100));
      updateStats([...detectedAnomalies, ...anomalies]);
    }

    return detectedAnomalies;
  };

  const detectSeverityAnomalies = (scan, findings) => {
    const anomalies = [];
    
    // High concentration of critical findings
    const criticalCount = findings.filter(f => f.severity === "CRITICAL").length;
    if (criticalCount >= 5) {
      anomalies.push({
        id: `severity_${scan.id || scan.scan_id}_critical`,
        type: "Severity Concentration",
        description: `Unusually high concentration of ${criticalCount} critical findings`,
        severity: "CRITICAL",
        target: scan.target,
        scan_type: scan.scan_type,
        timestamp: scan.timestamp || new Date().toISOString(),
        confidence: 0.9,
        metrics: {
          critical_findings: criticalCount,
          total_findings: findings.length,
          concentration_ratio: (criticalCount / findings.length * 100).toFixed(1)
        },
        recommendation: "Immediate security assessment required. Consider isolating affected systems."
      });
    }

    // Mixed severity patterns
    const severityDistribution = findings.reduce((acc, f) => {
      acc[f.severity] = (acc[f.severity] || 0) + 1;
      return acc;
    }, {});

    const hasMixedPattern = Object.keys(severityDistribution).length >= 3 && 
                             severityDistribution.CRITICAL > 0 && 
                             severityDistribution.LOW > 0;

    if (hasMixedPattern) {
      anomalies.push({
        id: `severity_${scan.id || scan.scan_id}_mixed`,
        type: "Mixed Severity Pattern",
        description: "Complex threat landscape with mixed severity levels detected",
        severity: "HIGH",
        target: scan.target,
        scan_type: scan.scan_type,
        timestamp: scan.timestamp || new Date().toISOString(),
        confidence: 0.7,
        metrics: severityDistribution,
        recommendation: "Comprehensive security assessment recommended. Prioritize critical issues."
      });
    }

    return anomalies;
  };

  const detectPatternAnomalies = (scan, findings) => {
    const anomalies = [];
    
    // Detect common vulnerability patterns
    const categories = findings.reduce((acc, f) => {
      acc[f.category] = (acc[f.category] || 0) + 1;
      return acc;
    }, {});

    // High concentration in specific category
    Object.entries(categories).forEach(([category, count]) => {
      if (count >= 3) {
        anomalies.push({
          id: `pattern_${scan.id || scan.scan_id}_${category}`,
          type: "Category Concentration",
          description: `${count} findings in ${category} category indicate systemic issue`,
          severity: count >= 5 ? "HIGH" : "MEDIUM",
          target: scan.target,
          scan_type: scan.scan_type,
          timestamp: scan.timestamp || new Date().toISOString(),
          confidence: 0.8,
          metrics: {
            category: category,
            count: count,
            percentage: ((count / findings.length) * 100).toFixed(1)
          },
          recommendation: `Focus remediation efforts on ${category} vulnerabilities.`
        });
      }
    });

    return anomalies;
  };

  const detectTemporalAnomalies = (scan, findings) => {
    const anomalies = [];
    
    // Scan duration anomalies (if available)
    if (scan.duration && scan.duration > 300000) { // 5 minutes
      anomalies.push({
        id: `temporal_${scan.id || scan.scan_id}_duration`,
        type: "Extended Scan Duration",
        description: `Scan took unusually long: ${Math.round(scan.duration / 60000)} minutes`,
        severity: "LOW",
        target: scan.target,
        scan_type: scan.scan_type,
        timestamp: scan.timestamp || new Date().toISOString(),
        confidence: 0.6,
        metrics: {
          duration_seconds: Math.round(scan.duration / 1000),
          finding_count: findings.length
        },
        recommendation: "Review scan configuration and target responsiveness."
      });
    }

    return anomalies;
  };

  const detectServiceAnomalies = (scan, findings) => {
    const anomalies = [];
    
    // Service-related anomalies
    if (scan.services && Array.isArray(scan.services)) {
      const serviceCount = scan.services.length;
      
      if (serviceCount > 20) {
        anomalies.push({
          id: `service_${scan.id || scan.scan_id}_count`,
          type: "High Service Count",
          description: `Unusually high number of services detected: ${serviceCount}`,
          severity: "MEDIUM",
          target: scan.target,
          scan_type: scan.scan_type,
          timestamp: scan.timestamp || new Date().toISOString(),
          confidence: 0.7,
          metrics: {
            service_count: serviceCount,
            open_ports: scan.open_ports?.length || 0
          },
          recommendation: "Review exposed services and disable unnecessary ones."
        });
      }
    }

    return anomalies;
  };

  const updateStats = (anomaliesList) => {
    const stats = {
      totalAnomalies: anomaliesList.length,
      criticalAnomalies: 0,
      highAnomalies: 0,
      mediumAnomalies: 0,
      lowAnomalies: 0,
      trend: "stable"
    };

    anomaliesList.forEach(anomaly => {
      switch (anomaly.severity?.toUpperCase()) {
        case 'CRITICAL':
          stats.criticalAnomalies++;
          break;
        case 'HIGH':
          stats.highAnomalies++;
          break;
        case 'MEDIUM':
          stats.mediumAnomalies++;
          break;
        case 'LOW':
          stats.lowAnomalies++;
          break;
      }
    });

    // Calculate trend (simplified)
    if (anomaliesList.length > 0) {
      const recentAnomalies = anomaliesList.filter(a => {
        const anomalyDate = new Date(a.timestamp);
        const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
        return anomalyDate > dayAgo;
      });
      
      if (recentAnomalies.length > stats.totalAnomalies * 0.5) {
        stats.trend = "increasing";
      } else if (recentAnomalies.length < stats.totalAnomalies * 0.2) {
        stats.trend = "decreasing";
      }
    }

    setStats(stats);
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

  const getAnomalyIcon = (type) => {
    switch (type) {
      case 'Severity Concentration': return '🚨';
      case 'Mixed Severity Pattern': return '🔀';
      case 'Category Concentration': return '📊';
      case 'Extended Scan Duration': return '⏱️';
      case 'High Service Count': return '🔧';
      default: return '⚠️';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  const formatDate = (date) => {
    if (!date) return "-";
    const now = new Date();
    const anomalyDate = new Date(date);
    const diff = now - anomalyDate;
    
    if (diff < 60000) return "Just now";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return anomalyDate.toLocaleDateString();
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
          background: "linear-gradient(135deg, #8b5cf6, #ec4899)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent"
        }}>
          🔍 Anomaly Detection
        </h2>
        <p style={{ color: "#94a3b8", marginBottom: "30px" }}>
          AI-powered anomaly detection and threat analysis
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "20px",
          marginBottom: "30px"
        }}
      >
        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>Total Anomalies</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#8b5cf6" }}>
            {stats.totalAnomalies}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Detected patterns</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>Critical</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#ef4444" }}>
            {stats.criticalAnomalies}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Immediate attention</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>High</h4>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: "#f97316" }}>
            {stats.highAnomalies}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Priority issues</p>
        </motion.div>

        <motion.div whileHover={{ scale: 1.05 }} style={cardStyle}>
          <h4>Trend {getTrendIcon(stats.trend)}</h4>
          <div style={{ fontSize: "24px", fontWeight: "bold", color: "#06b6d4" }}>
            {stats.trend}
          </div>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>Activity trend</p>
        </motion.div>
      </motion.div>

      {/* Time Range Selector */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        style={{ display: "flex", gap: "10px", marginBottom: "20px" }}
      >
        {["1h", "24h", "7d", "30d"].map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            style={{
              padding: "8px 16px",
              borderRadius: "8px",
              border: "1px solid rgba(255,255,255,0.2)",
              background: timeRange === range ? "#8b5cf6" : "transparent",
              color: "#fff",
              cursor: "pointer",
              transition: "all 0.3s ease",
              fontWeight: timeRange === range ? "bold" : "normal"
            }}
          >
            {range === "1h" && "Last Hour"}
            {range === "24h" && "Last 24h"}
            {range === "7d" && "Last 7 days"}
            {range === "30d" && "Last 30 days"}
          </button>
        ))}
      </motion.div>

      {/* Anomalies List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        style={cardStyle}
      >
        <h3 style={{ marginBottom: "20px" }}>🔍 Detected Anomalies</h3>
        
        {loading ? (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <div style={{ 
              width: "40px", 
              height: "40px", 
              border: "4px solid #334155", 
              borderTop: "4px solid #8b5cf6",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              margin: "0 auto"
            }} />
            <p style={{ marginTop: "10px", color: "#94a3b8" }}>Analyzing for anomalies...</p>
          </div>
        ) : anomalies.length === 0 ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>✨</div>
            <h3>No Anomalies Detected</h3>
            <p>System behavior appears normal</p>
          </div>
        ) : (
          <div style={{ maxHeight: "600px", overflowY: "auto" }}>
            {anomalies.map((anomaly, index) => (
              <motion.div
                key={anomaly.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                style={{
                  padding: "15px",
                  marginBottom: "12px",
                  borderRadius: "8px",
                  background: "rgba(255,255,255,0.05)",
                  border: `1px solid ${getSeverityColor(anomaly.severity)}40`,
                  borderLeft: `4px solid ${getSeverityColor(anomaly.severity)}`,
                  cursor: "pointer"
                }}
                whileHover={{ scale: 1.02, background: "rgba(255,255,255,0.08)" }}
                onClick={() => setSelectedAnomaly(anomaly)}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                      <span style={{ fontSize: "18px" }}>
                        {getAnomalyIcon(anomaly.type)}
                      </span>
                      <h4 style={{ margin: 0, fontSize: "16px" }}>
                        {anomaly.type}
                      </h4>
                      <span style={{
                        background: getSeverityColor(anomaly.severity),
                        color: "#fff",
                        padding: "2px 8px",
                        borderRadius: "12px",
                        fontSize: "10px",
                        fontWeight: "bold"
                      }}>
                        {anomaly.severity}
                      </span>
                    </div>
                    
                    <p style={{ 
                      margin: "0 0 8px 0", 
                      fontSize: "14px", 
                      color: "#94a3b8",
                      lineHeight: 1.4
                    }}>
                      {anomaly.description}
                    </p>
                    
                    <div style={{ display: "flex", gap: "15px", fontSize: "12px", color: "#94a3b8" }}>
                      <span>🎯 {anomaly.target}</span>
                      <span>🔍 {anomaly.scan_type?.toUpperCase()}</span>
                      <span>⏰ {formatDate(anomaly.timestamp)}</span>
                      <span>📊 {Math.round(anomaly.confidence * 100)}% confidence</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Anomaly Details Modal */}
      {selectedAnomaly && (
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
          onClick={() => setSelectedAnomaly(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            style={{
              background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
              padding: "30px",
              borderRadius: "16px",
              maxWidth: "600px",
              maxHeight: "80vh",
              overflowY: "auto",
              border: "1px solid rgba(255,255,255,0.1)"
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h3>{getAnomalyIcon(selectedAnomaly.type)} {selectedAnomaly.type}</h3>
              <button
                onClick={() => setSelectedAnomaly(null)}
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
              <p><strong>Target:</strong> {selectedAnomaly.target}</p>
              <p><strong>Severity:</strong> <span style={{ color: getSeverityColor(selectedAnomaly.severity) }}>{selectedAnomaly.severity}</span></p>
              <p><strong>Confidence:</strong> {Math.round(selectedAnomaly.confidence * 100)}%</p>
              <p><strong>Detected:</strong> {formatDate(selectedAnomaly.timestamp)}</p>
            </div>

            <div style={{ marginBottom: "20px" }}>
              <h4>Description</h4>
              <p style={{ color: "#94a3b8" }}>{selectedAnomaly.description}</p>
            </div>

            {selectedAnomaly.metrics && (
              <div style={{ marginBottom: "20px" }}>
                <h4>Metrics</h4>
                <div style={{ display: "grid", gap: "10px" }}>
                  {Object.entries(selectedAnomaly.metrics).map(([key, value]) => (
                    <div key={key} style={{
                      display: "flex",
                      justifyContent: "space-between",
                      padding: "8px",
                      background: "rgba(255,255,255,0.05)",
                      borderRadius: "4px"
                    }}>
                      <span style={{ color: "#94a3b8" }}>{key}:</span>
                      <span style={{ fontWeight: "bold" }}>{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedAnomaly.recommendation && (
              <div>
                <h4>Recommendation</h4>
                <div style={{
                  padding: "12px",
                  background: "rgba(139, 92, 246, 0.1)",
                  borderRadius: "8px",
                  border: "1px solid rgba(139, 92, 246, 0.3)"
                }}>
                  {selectedAnomaly.recommendation}
                </div>
              </div>
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
          </motion.div>
        </motion.div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
