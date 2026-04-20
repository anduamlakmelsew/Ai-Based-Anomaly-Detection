import React, { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getScanById } from "../../services/scanService";

const severityColors = {
  CRITICAL: "#dc2626",
  HIGH: "#f59e0b", 
  MEDIUM: "#facc15",
  LOW: "#16a34a",
  INFO: "#3b82f6",
};

const EnhancedScanResult = ({ result }) => {
  const [scanDetails, setScanDetails] = useState(result || null);
  const [activeTab, setActiveTab] = useState("overview");
  const scanId = result?.scan_id ?? result?.id;

  useEffect(() => {
    let isMounted = true;

    const loadFromDb = async () => {
      if (!scanId) return;
      try {
        const res = await getScanById(scanId);
        const data = res?.data || res?.result || res;
        if (isMounted) setScanDetails(data);
      } catch (e) {
        console.error("Failed to fetch scan details:", e);
      }
    };

    loadFromDb();
    return () => {
      isMounted = false;
    };
  }, [scanId]);

  useEffect(() => {
    setScanDetails(result || null);
  }, [result]);

  const {
    target,
    scan_type,
    risk = { score: 0, level: "LOW", explanation: "No data" },
    findings = [],
    web_scan,
    open_ports = [],
    services = [],
    os_info = {},
    system_data = {},
    total_urls_scanned = 0,
  } = useMemo(() => scanDetails || {}, [scanDetails]);

  if (!scanDetails) return (
    <div style={{ 
      padding: "40px", 
      textAlign: "center", 
      color: "#94a3b8",
      background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
      borderRadius: "16px",
      border: "1px solid rgba(255,255,255,0.1)"
    }}>
      <div style={{ fontSize: "48px", marginBottom: "16px" }}>🔍</div>
      <h3>No Scan Selected</h3>
      <p>Start a new scan or select an existing scan to view detailed results</p>
    </div>
  );

  // Group findings by severity
  const groupedFindings = findings.reduce((acc, f) => {
    const sev = f.severity || "LOW";
    if (!acc[sev]) acc[sev] = [];
    acc[sev].push(f);
    return acc;
  }, {});

  const getScanTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'network': return '🌐';
      case 'system': return '🖥️';
      case 'web': return '🌍';
      default: return '🔍';
    }
  };

  const getRiskColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MEDIUM': return '#eab308';
      case 'LOW': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const cardStyle = {
    background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
    padding: "20px",
    borderRadius: "12px",
    border: "1px solid rgba(255,255,255,0.1)",
    marginBottom: "20px"
  };

  const tabStyle = (isActive) => ({
    padding: "8px 16px",
    borderRadius: "8px",
    border: "none",
    background: isActive ? "#3b82f6" : "transparent",
    color: "#fff",
    cursor: "pointer",
    transition: "all 0.3s ease",
    fontWeight: isActive ? "bold" : "normal"
  });

  return (
    <div style={{ color: "#fff" }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: "20px" }}
      >
        <h2 style={{ fontSize: "28px", marginBottom: "10px" }}>
          {getScanTypeIcon(scan_type)} Scan Results
        </h2>
        <div style={{ display: "flex", gap: "20px", fontSize: "14px", color: "#94a3b8" }}>
          <span><strong>Target:</strong> {target}</span>
          <span><strong>Type:</strong> {scan_type?.toUpperCase()}</span>
          <span><strong>ID:</strong> #{scanId}</span>
        </div>
      </motion.div>

      {/* Navigation Tabs */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}
      >
        {["overview", "findings", scan_type].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={tabStyle(activeTab === tab)}
          >
            {tab === "overview" && "📊 Overview"}
            {tab === "findings" && "🚨 Findings"}
            {tab === "network" && "🌐 Network"}
            {tab === "system" && "🖥️ System"}
            {tab === "web" && "🌍 Web"}
          </button>
        ))}
      </motion.div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {/* Overview Tab */}
          {activeTab === "overview" && (
            <div>
              {/* Risk Summary */}
              <motion.div
                initial={{ scale: 0.95 }}
                animate={{ scale: 1 }}
                style={{
                  ...cardStyle,
                  borderLeft: `4px solid ${getRiskColor(risk.level)}`,
                  background: `linear-gradient(135deg, #1e293b 0%, ${getRiskColor(risk.level)}20 100%)`
                }}
              >
                <h3 style={{ marginBottom: "15px" }}>⚠️ Risk Assessment</h3>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "15px" }}>
                  <div>
                    <div style={{ fontSize: "32px", fontWeight: "bold", color: getRiskColor(risk.level) }}>
                      {risk.score}
                    </div>
                    <div style={{ fontSize: "12px", color: "#94a3b8" }}>Risk Score</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: getRiskColor(risk.level) }}>
                      {risk.level}
                    </div>
                    <div style={{ fontSize: "12px", color: "#94a3b8" }}>Risk Level</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: "#fff" }}>
                      {findings.length}
                    </div>
                    <div style={{ fontSize: "12px", color: "#94a3b8" }}>Total Findings</div>
                  </div>
                </div>
                <p style={{ marginTop: "15px", fontSize: "14px" }}>
                  {risk.explanation}
                </p>
              </motion.div>

              {/* Quick Stats */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
                {open_ports.length > 0 && (
                  <motion.div style={cardStyle}>
                    <h4>🌐 Open Ports</h4>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: "#3b82f6" }}>
                      {open_ports.length}
                    </div>
                    <p style={{ fontSize: "12px", color: "#94a3b8" }}>Ports detected</p>
                  </motion.div>
                )}
                
                {services.length > 0 && (
                  <motion.div style={cardStyle}>
                    <h4>🔧 Services</h4>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: "#8b5cf6" }}>
                      {services.length}
                    </div>
                    <p style={{ fontSize: "12px", color: "#94a3b8" }}>Services found</p>
                  </motion.div>
                )}

                {total_urls_scanned > 0 && (
                  <motion.div style={cardStyle}>
                    <h4>🔗 URLs</h4>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: "#06b6d4" }}>
                      {total_urls_scanned}
                    </div>
                    <p style={{ fontSize: "12px", color: "#94a3b8" }}>URLs scanned</p>
                  </motion.div>
                )}
              </div>
            </div>
          )}

          {/* Findings Tab */}
          {activeTab === "findings" && (
            <div>
              <h3 style={{ marginBottom: "20px" }}>🚨 Security Findings</h3>
              {Object.keys(groupedFindings).length === 0 ? (
                <div style={{ 
                  textAlign: "center", 
                  padding: "40px",
                  background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
                  borderRadius: "12px",
                  border: "1px solid rgba(255,255,255,0.1)"
                }}>
                  <div style={{ fontSize: "48px", marginBottom: "16px" }}>✅</div>
                  <h3>No Vulnerabilities Found</h3>
                  <p style={{ color: "#94a3b8" }}>Great! No security issues were detected.</p>
                </div>
              ) : (
                Object.keys(severityColors).map((level) => {
                  const items = groupedFindings[level];
                  if (!items || items.length === 0) return null;

                  return (
                    <motion.div
                      key={level}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                      style={{ marginBottom: "20px" }}
                    >
                      <h4 style={{ 
                        color: severityColors[level], 
                        marginBottom: "10px",
                        display: "flex",
                        alignItems: "center",
                        gap: "10px"
                      }}>
                        <span style={{ 
                          background: severityColors[level], 
                          color: "#fff",
                          padding: "4px 12px",
                          borderRadius: "20px",
                          fontSize: "14px"
                        }}>
                          {level}
                        </span>
                        <span>({items.length} findings)</span>
                      </h4>
                      {items.map((v, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.05 }}
                          style={{
                            border: `1px solid ${severityColors[level]}40`,
                            padding: "15px",
                            borderRadius: "8px",
                            marginBottom: "10px",
                            background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
                            borderLeft: `3px solid ${severityColors[level]}`
                          }}
                        >
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                            <h5 style={{ margin: 0, color: "#fff" }}>
                              {v.type || "Unknown"}
                            </h5>
                            <span style={{ 
                              fontSize: "12px", 
                              color: "#94a3b8",
                              background: "rgba(255,255,255,0.1)",
                              padding: "2px 8px",
                              borderRadius: "4px"
                            }}>
                              {v.confidence || "MEDIUM"} confidence
                            </span>
                          </div>
                          <p style={{ margin: "8px 0", color: "#94a3b8", fontSize: "14px" }}>
                            {v.evidence || v.description || "No evidence available"}
                          </p>
                          {v.url && (
                            <p style={{ margin: "4px 0", fontSize: "12px", color: "#3b82f6" }}>
                              📍 {v.url}
                            </p>
                          )}
                          {v.exploits_available && v.exploits_available.length > 0 && (
                            <p style={{ margin: "4px 0", fontSize: "12px", color: "#ef4444" }}>
                              ⚠️ Exploits available: {v.exploits_available.length}
                            </p>
                          )}
                          {v.remediation && (
                            <div style={{ 
                              marginTop: "8px", 
                              padding: "8px", 
                              background: "rgba(34, 197, 94, 0.1)",
                              borderRadius: "4px",
                              fontSize: "12px",
                              border: "1px solid rgba(34, 197, 94, 0.3)"
                            }}>
                              <strong>Fix:</strong> {v.remediation}
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </motion.div>
                  );
                })
              )}
            </div>
          )}

          {/* Network Scanner Details */}
          {activeTab === "network" && (
            <div>
              <h3 style={{ marginBottom: "20px" }}>🌐 Network Scan Details</h3>
              
              {/* Open Ports */}
              {open_ports.length > 0 && (
                <motion.div style={cardStyle}>
                  <h4>🔓 Open Ports ({open_ports.length})</h4>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "10px" }}>
                    {open_ports.map((port) => (
                      <span key={port} style={{
                        background: "#3b82f6",
                        color: "#fff",
                        padding: "4px 8px",
                        borderRadius: "4px",
                        fontSize: "12px"
                      }}>
                        {port}
                      </span>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Services */}
              {services.length > 0 && (
                <motion.div style={cardStyle}>
                  <h4>🔧 Detected Services ({services.length})</h4>
                  <div style={{ marginTop: "10px" }}>
                    {services.map((service, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "10px",
                          background: "rgba(255,255,255,0.05)",
                          borderRadius: "6px",
                          marginBottom: "8px",
                          border: "1px solid rgba(255,255,255,0.1)"
                        }}
                      >
                        <div>
                          <span style={{ fontWeight: "bold", color: "#fff" }}>
                            {service.service || "Unknown"}
                          </span>
                          <span style={{ margin: "0 10px", color: "#94a3b8" }}>
                            Port {service.port}
                          </span>
                          {service.version && (
                            <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                              {service.version}
                            </span>
                          )}
                        </div>
                        <span style={{
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "10px",
                          background: service.state === "open" ? "#22c55e" : "#ef4444",
                          color: "#fff"
                        }}>
                          {service.state}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          )}

          {/* System Scanner Details */}
          {activeTab === "system" && (
            <div>
              <h3 style={{ marginBottom: "20px" }}>🖥️ System Scan Details</h3>
              
              {/* OS Information */}
              {system_data?.os_info && (
                <motion.div style={cardStyle}>
                  <h4>💻 Operating System</h4>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px", marginTop: "10px" }}>
                    <div>
                      <span style={{ color: "#94a3b8", fontSize: "12px" }}>System:</span>
                      <div style={{ fontWeight: "bold" }}>{system_data.os_info.system}</div>
                    </div>
                    <div>
                      <span style={{ color: "#94a3b8", fontSize: "12px" }}>Release:</span>
                      <div style={{ fontWeight: "bold" }}>{system_data.os_info.release}</div>
                    </div>
                    <div>
                      <span style={{ color: "#94a3b8", fontSize: "12px" }}>Architecture:</span>
                      <div style={{ fontWeight: "bold" }}>{system_data.os_info.architecture}</div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Services */}
              {system_data?.services && system_data.services.length > 0 && (
                <motion.div style={cardStyle}>
                  <h4>🔧 Running Services ({system_data.services.length})</h4>
                  <div style={{ 
                    maxHeight: "200px", 
                    overflowY: "auto",
                    marginTop: "10px"
                  }}>
                    {system_data.services.map((service, index) => (
                      <div key={index} style={{
                        padding: "6px 10px",
                        background: "rgba(255,255,255,0.05)",
                        borderRadius: "4px",
                        marginBottom: "4px",
                        fontSize: "13px",
                        border: "1px solid rgba(255,255,255,0.05)"
                      }}>
                        {service}
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* System Stats */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "15px" }}>
                {system_data?.packages_count && (
                  <motion.div style={cardStyle}>
                    <h4>📦 Packages</h4>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: "#8b5cf6" }}>
                      {system_data.packages_count}
                    </div>
                  </motion.div>
                )}
                
                {system_data?.processes_count && (
                  <motion.div style={cardStyle}>
                    <h4>⚙️ Processes</h4>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: "#f59e0b" }}>
                      {system_data.processes_count}
                    </div>
                  </motion.div>
                )}

                {system_data?.users && (
                  <motion.div style={cardStyle}>
                    <h4>👤 Users</h4>
                    <div style={{ fontSize: "24px", fontWeight: "bold", color: "#06b6d4" }}>
                      {system_data.users.length}
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          )}

          {/* Web Scanner Details */}
          {activeTab === "web" && (
            <div>
              <h3 style={{ marginBottom: "20px" }}>🌍 Web Application Scan Details</h3>
              
              {/* Web Scan Results */}
              {web_scan && (
                <>
                  {/* Basic Info */}
                  <motion.div style={cardStyle}>
                    <h4>📄 Application Information</h4>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px", marginTop: "10px" }}>
                      <div>
                        <span style={{ color: "#94a3b8", fontSize: "12px" }}>Status Code:</span>
                        <div style={{ fontWeight: "bold" }}>{web_scan.status_code || "N/A"}</div>
                      </div>
                      <div>
                        <span style={{ color: "#94a3b8", fontSize: "12px" }}>Title:</span>
                        <div style={{ fontWeight: "bold" }}>{web_scan.title || "N/A"}</div>
                      </div>
                      <div>
                        <span style={{ color: "#94a3b8", fontSize: "12px" }}>Mode:</span>
                        <div style={{ fontWeight: "bold" }}>{web_scan.mode || "N/A"}</div>
                      </div>
                    </div>
                  </motion.div>

                  {/* Technologies */}
                  {web_scan.recon?.technologies && web_scan.recon.technologies.length > 0 && (
                    <motion.div style={cardStyle}>
                      <h4>🛠️ Detected Technologies</h4>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "10px" }}>
                        {web_scan.recon.technologies.map((tech, index) => (
                          <span key={index} style={{
                            background: "#06b6d4",
                            color: "#fff",
                            padding: "4px 12px",
                            borderRadius: "20px",
                            fontSize: "12px"
                          }}>
                            {tech}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* URLs Discovered */}
                  {web_scan.recon?.links && web_scan.recon.links.length > 0 && (
                    <motion.div style={cardStyle}>
                      <h4>🔗 Discovered URLs ({web_scan.recon.links.length})</h4>
                      <div style={{ 
                        maxHeight: "200px", 
                        overflowY: "auto",
                        marginTop: "10px"
                      }}>
                        {web_scan.recon.links.map((link, index) => (
                          <div key={index} style={{
                            padding: "6px 10px",
                            background: "rgba(255,255,255,0.05)",
                            borderRadius: "4px",
                            marginBottom: "4px",
                            fontSize: "12px",
                            color: "#3b82f6",
                            border: "1px solid rgba(255,255,255,0.05)"
                          }}>
                            {link}
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </>
              )}
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default EnhancedScanResult;
