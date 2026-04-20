import { motion, AnimatePresence } from "framer-motion";

export default function EnhancedActivityLog({ scans }) {
  const recentScans = scans?.slice(0, 8) || [];

  const getScanTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'network': return '🌐';
      case 'system': return '🖥️';
      case 'web': return '🌍';
      default: return '🔍';
    }
  };

  const getScanTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'network': return '#3b82f6';
      case 'system': return '#8b5cf6';
      case 'web': return '#06b6d4';
      default: return '#6b7280';
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return '#22c55e';
      case 'running': return '#f59e0b';
      case 'failed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getRiskColor = (score) => {
    if (score >= 70) return '#ef4444';
    if (score >= 50) return '#f97316';
    if (score >= 30) return '#eab308';
    return '#22c55e';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return "Just now";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div>
      <h4 style={{ marginBottom: "20px" }}>📋 Recent Activity</h4>
      
      {recentScans.length === 0 ? (
        <div style={{ 
          textAlign: "center", 
          padding: "40px",
          color: "#94a3b8",
          fontSize: "14px"
        }}>
          No recent activity. Start scanning to see activity logs.
        </div>
      ) : (
        <div style={{ maxHeight: "400px", overflowY: "auto" }}>
          <AnimatePresence>
            {recentScans.map((scan, index) => (
              <motion.div
                key={scan.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  padding: "12px",
                  marginBottom: "8px",
                  background: "rgba(255,255,255,0.03)",
                  borderRadius: "8px",
                  border: "1px solid rgba(255,255,255,0.05)",
                  fontSize: "13px",
                  cursor: "pointer"
                }}
                whileHover={{ 
                  background: "rgba(255,255,255,0.08)",
                  transform: "translateX(5px)"
                }}
              >
                {/* Scan Type Icon */}
                <div style={{
                  width: "32px",
                  height: "32px",
                  borderRadius: "8px",
                  background: getScanTypeColor(scan.scan_type),
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginRight: "12px",
                  fontSize: "16px"
                }}>
                  {getScanTypeIcon(scan.scan_type)}
                </div>

                {/* Main Content */}
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    display: "flex", 
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "4px"
                  }}>
                    <span style={{ fontWeight: "600" }}>
                      {scan.scan_type?.toUpperCase()} Scan
                    </span>
                    <span style={{ 
                      fontSize: "11px", 
                      color: "#94a3b8",
                      textTransform: "uppercase"
                    }}>
                      {formatTime(scan.timestamp)}
                    </span>
                  </div>
                  
                  <div style={{ 
                    color: "#94a3b8", 
                    fontSize: "12px",
                    marginBottom: "6px"
                  }}>
                    Target: {scan.target}
                  </div>

                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    {/* Status Badge */}
                    <span style={{
                      padding: "2px 6px",
                      borderRadius: "4px",
                      fontSize: "10px",
                      fontWeight: "bold",
                      background: getStatusColor(scan.status),
                      color: "#fff"
                    }}>
                      {scan.status}
                    </span>

                    {/* Findings Count */}
                    {scan.total_findings > 0 && (
                      <span style={{
                        padding: "2px 6px",
                        borderRadius: "4px",
                        fontSize: "10px",
                        background: "rgba(255,255,255,0.1)",
                        color: "#fff"
                      }}>
                        {scan.total_findings} findings
                      </span>
                    )}

                    {/* Risk Score */}
                    <span style={{
                      padding: "2px 6px",
                      borderRadius: "4px",
                      fontSize: "10px",
                      fontWeight: "bold",
                      background: getRiskColor(scan.risk?.score || 0),
                      color: "#fff"
                    }}>
                      Risk: {scan.risk?.score || 0}
                    </span>
                  </div>
                </div>

                {/* Progress Indicator */}
                {scan.status === "running" && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    style={{
                      width: "16px",
                      height: "16px",
                      border: "2px solid rgba(255,255,255,0.3)",
                      borderTop: "2px solid #f59e0b",
                      borderRadius: "50%",
                      marginLeft: "8px"
                    }}
                  />
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Summary Footer */}
      {recentScans.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          style={{
            marginTop: "15px",
            padding: "12px",
            background: "rgba(255,255,255,0.05)",
            borderRadius: "8px",
            fontSize: "12px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >
          <span style={{ color: "#94a3b8" }}>
            Showing {recentScans.length} most recent scans
          </span>
          <div style={{ display: "flex", gap: "15px" }}>
            <div>
              <span style={{ color: "#22c55e" }}>
                {recentScans.filter(s => s.status === "completed").length}
              </span>{" "}
              completed
            </div>
            <div>
              <span style={{ color: "#f59e0b" }}>
                {recentScans.filter(s => s.status === "running").length}
              </span>{" "}
              running
            </div>
            <div>
              <span style={{ color: "#ef4444" }}>
                {recentScans.filter(s => s.status === "failed").length}
              </span>{" "}
              failed
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
