import { motion } from "framer-motion";

export default function EnhancedTrafficChart({ scans }) {
  // Process scan data for chart
  const scanData = scans?.slice(0, 10).map((scan, index) => ({
    name: `Scan ${scan.id}`,
    risk: scan.risk?.score || 0,
    findings: scan.total_findings || 0,
    type: scan.scan_type || "unknown",
    date: new Date(scan.timestamp).toLocaleDateString()
  }));

  const maxRisk = Math.max(...scanData.map(d => d.risk), 100);
  const maxFindings = Math.max(...scanData.map(d => d.findings), 10);

  const getScanTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'network': return '#3b82f6';
      case 'system': return '#8b5cf6';
      case 'web': return '#06b6d4';
      default: return '#6b7280';
    }
  };

  const getRiskColor = (score) => {
    if (score >= 70) return '#ef4444';
    if (score >= 50) return '#f97316';
    if (score >= 30) return '#eab308';
    return '#22c55e';
  };

  return (
    <div>
      <h4 style={{ marginBottom: "20px" }}>📈 Scan Activity & Risk Trends</h4>
      
      {scanData.length === 0 ? (
        <div style={{ 
          textAlign: "center", 
          padding: "40px",
          color: "#94a3b8",
          fontSize: "14px"
        }}>
          No scan data available. Start scanning to see activity trends.
        </div>
      ) : (
        <div>
          {/* Chart Legend */}
          <div style={{ 
            display: "flex", 
            justifyContent: "center", 
            gap: "20px",
            marginBottom: "20px",
            fontSize: "12px"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <div style={{ width: "12px", height: "12px", background: "#3b82f6", borderRadius: "2px" }} />
              <span>Network</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <div style={{ width: "12px", height: "12px", background: "#8b5cf6", borderRadius: "2px" }} />
              <span>System</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <div style={{ width: "12px", height: "12px", background: "#06b6d4", borderRadius: "2px" }} />
              <span>Web</span>
            </div>
          </div>

          {/* Chart Container */}
          <div style={{ 
            position: "relative",
            height: "250px",
            background: "rgba(255,255,255,0.02)",
            borderRadius: "12px",
            padding: "20px",
            border: "1px solid rgba(255,255,255,0.1)"
          }}>
            {/* Y-axis labels */}
            <div style={{ 
              position: "absolute",
              left: "0",
              top: "20px",
              bottom: "40px",
              width: "40px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              fontSize: "10px",
              color: "#94a3b8"
            }}>
              <span>100</span>
              <span>75</span>
              <span>50</span>
              <span>25</span>
              <span>0</span>
            </div>

            {/* Chart bars */}
            <div style={{ 
              marginLeft: "50px",
              marginRight: "20px",
              height: "100%",
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "space-around",
              gap: "8px"
            }}>
              {scanData.map((data, index) => (
                <motion.div
                  key={data.name}
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: `${(data.risk / maxRisk) * 180}px`, opacity: 1 }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  style={{
                    position: "relative",
                    flex: 1,
                    background: getScanTypeColor(data.type),
                    borderRadius: "4px 4px 0 0",
                    cursor: "pointer",
                    maxWidth: "40px"
                  }}
                  whileHover={{ scale: 1.05 }}
                  title={`${data.name}: Risk ${data.risk}, Findings ${data.findings}`}
                >
                  {/* Risk score on top of bar */}
                  <div style={{
                    position: "absolute",
                    top: "-20px",
                    left: "50%",
                    transform: "translateX(-50%)",
                    fontSize: "10px",
                    fontWeight: "bold",
                    color: getRiskColor(data.risk)
                  }}>
                    {data.risk}
                  </div>
                  
                  {/* Findings count inside bar */}
                  {data.findings > 0 && (
                    <div style={{
                      position: "absolute",
                      bottom: "5px",
                      left: "50%",
                      transform: "translateX(-50%)",
                      fontSize: "9px",
                      color: "#fff",
                      background: "rgba(0,0,0,0.3)",
                      padding: "2px 4px",
                      borderRadius: "2px"
                    }}>
                      {data.findings}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>

            {/* X-axis labels */}
            <div style={{ 
              position: "absolute",
              bottom: "10px",
              left: "50px",
              right: "20px",
              display: "flex",
              justifyContent: "space-around",
              fontSize: "10px",
              color: "#94a3b8"
            }}>
              {scanData.map((data) => (
                <div key={data.name} style={{ textAlign: "center" }}>
                  <div>{data.id}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Summary Stats */}
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
            gap: "15px",
            marginTop: "20px"
          }}>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              style={{
                background: "rgba(255,255,255,0.05)",
                padding: "12px",
                borderRadius: "8px",
                textAlign: "center"
              }}
            >
              <div style={{ fontSize: "20px", fontWeight: "bold", color: "#3b82f6" }}>
                {scanData.length}
              </div>
              <div style={{ fontSize: "12px", color: "#94a3b8" }}>Total Scans</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              style={{
                background: "rgba(255,255,255,0.05)",
                padding: "12px",
                borderRadius: "8px",
                textAlign: "center"
              }}
            >
              <div style={{ fontSize: "20px", fontWeight: "bold", color: "#f97316" }}>
                {scanData.reduce((sum, d) => sum + d.findings, 0)}
              </div>
              <div style={{ fontSize: "12px", color: "#94a3b8" }}>Total Findings</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              style={{
                background: "rgba(255,255,255,0.05)",
                padding: "12px",
                borderRadius: "8px",
                textAlign: "center"
              }}
            >
              <div style={{ fontSize: "20px", fontWeight: "bold", color: getRiskColor(scanData.reduce((sum, d) => sum + d.risk, 0) / scanData.length) }}>
                {Math.round(scanData.reduce((sum, d) => sum + d.risk, 0) / scanData.length) || 0}
              </div>
              <div style={{ fontSize: "12px", color: "#94a3b8" }}>Avg Risk Score</div>
            </motion.div>
          </div>
        </div>
      )}
    </div>
  );
}
