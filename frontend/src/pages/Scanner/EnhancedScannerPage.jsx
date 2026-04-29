import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import { motion, AnimatePresence } from "framer-motion";
import ScanForm from "./ScanForm";
import ScanHistory from "./ScanHistory";
import ScanResult from "./ScanResult";
import EnhancedScanResult from "./EnhancedScanResult";
import { discoverHosts } from "../../services/scanService";
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

export default function EnhancedScannerPage() {
  const navigate = useNavigate();
  const [selectedScan, setSelectedScan] = useState(null);
  const [liveScan, setLiveScan] = useState(null);
  const [range, setRange] = useState("192.168.1.0/24");
  const [discovering, setDiscovering] = useState(false);
  const [discoverError, setDiscoverError] = useState("");
  const [hosts, setHosts] = useState([]);
  const [activeTab, setActiveTab] = useState("scan");
  const [scanStats, setScanStats] = useState({
    totalScans: 0,
    criticalFindings: 0,
    highFindings: 0,
    mediumFindings: 0
  });
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const stopScan = () => {
    if (!socket || !liveScan) {
      console.log("Cannot stop scan: socket or liveScan not available");
      return;
    }
    
    // Confirm before stopping
    if (window.confirm("Are you sure you want to stop the current scan?")) {
      console.log("🛑 Stopping scan:", liveScan.scan_id);
      
      // Emit stop scan event to backend
      socket.emit("stop_scan", { scan_id: liveScan.scan_id });
      
      // Show immediate feedback (will be updated by socket event)
      console.log("📡 Stop scan request sent");
    }
  };

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    if (!socket) return;

    const onProgress = (data) => {
      setLiveScan(data);
    };

    const onScanStopped = (data) => {
      console.log("🛑 Scan stopped:", data);
      if (data.success) {
        setLiveScan(null);
        // Optionally show a notification
        console.log("✅ Scan stopped successfully");
      } else {
        console.error("❌ Failed to stop scan:", data.message);
      }
    };

    const onScanCompleted = (data) => {
      console.log("🎉 Scan completed:", data);
      // Clear live scan when completed
      setLiveScan(null);
      // Trigger refresh of scan history and results
      setRefreshTrigger(prev => prev + 1);
      console.log("✅ Scan completed successfully - refreshing data");
    };

    socket.on("scan_progress", onProgress);
    socket.on("scan_stopped", onScanStopped);
    socket.on("scan_completed", onScanCompleted);

    return () => {
      socket.off("scan_progress", onProgress);
      socket.off("scan_stopped", onScanStopped);
      socket.off("scan_completed", onScanCompleted);
    };
  }, []);

  const handleDiscover = async () => {
    if (!range) {
      setDiscoverError("IP range is required");
      return;
    }

    if (!getToken()) {
      setDiscoverError("Please login first to use network discovery");
      return;
    }

    setDiscoverError("");
    setDiscovering(true);

    try {
      const data = await discoverHosts(range);
      if (!data?.success) {
        setDiscoverError(data?.error || "Discovery failed");
        setHosts([]);
      } else {
        setHosts(data.hosts || []);
      }
    } catch (e) {
      console.error("Discovery error:", e);
      setDiscoverError("Discovery failed. Check backend logs.");
      setHosts([]);
    } finally {
      setDiscovering(false);
    }
  };

  const cardStyle = {
    background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
    padding: "20px",
    borderRadius: "16px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1)",
    color: "#fff",
    border: "1px solid rgba(255,255,255,0.1)",
    backdropFilter: "blur(10px)",
    transition: "all 0.3s ease"
  };

  const tabStyle = (isActive) => ({
    padding: "10px 20px",
    borderRadius: "10px",
    border: "none",
    background: isActive ? "#3b82f6" : "transparent",
    color: "#fff",
    cursor: "pointer",
    transition: "all 0.3s ease",
    fontWeight: isActive ? "bold" : "normal"
  });

  return (
    <div style={{ 
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
          🔍 Security Scanner
        </h2>
        <p style={{ color: "#94a3b8", marginBottom: "30px" }}>
          Comprehensive vulnerability assessment for networks, systems, and web applications
        </p>
      </motion.div>

      {/* Navigation Tabs */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        style={{ display: "flex", gap: "10px", marginBottom: "30px" }}
      >
        {["scan", "discovery", "history", "results"].map((tab) => (
          <motion.button
            key={tab}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab(tab)}
            style={tabStyle(activeTab === tab)}
          >
            {tab === "scan" && "🚀 New Scan"}
            {tab === "discovery" && "🌐 Network Discovery"}
            {tab === "history" && "📜 Scan History"}
            {tab === "results" && "📊 Results"}
          </motion.button>
        ))}
      </motion.div>

      {/* Live Scan Banner */}
      <AnimatePresence>
        {liveScan && (liveScan.status === "running" || liveScan.status === "initializing") && (
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
              <h4 style={{ margin: 0 }}>⚡ Live Scan in Progress</h4>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={stopScan}
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
                🛑 Stop Scan
              </motion.button>
            </div>
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

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === "scan" && (
            <div>
              <ScanForm onScanComplete={setSelectedScan} />
              {selectedScan && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{ marginTop: "20px" }}
                >
                  <EnhancedScanResult result={selectedScan} />
                </motion.div>
              )}
            </div>
          )}

          {activeTab === "discovery" && (
            <motion.div
              style={cardStyle}
              whileHover={{ scale: 1.01 }}
            >
              <h4 style={{ marginBottom: "20px" }}>🌐 Network Discovery</h4>
              <p style={{ margin: "0 0 15px", fontSize: "14px", color: "#94a3b8" }}>
                Enter an IP range (CIDR) to find active devices before running a scan.
              </p>

              <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
                <input
                  type="text"
                  value={range}
                  onChange={(e) => setRange(e.target.value)}
                  placeholder="e.g. 192.168.1.0/24"
                  style={{
                    flex: 1,
                    padding: "10px 15px",
                    borderRadius: "8px",
                    border: "1px solid rgba(255,255,255,0.2)",
                    background: "rgba(255,255,255,0.1)",
                    color: "#fff",
                    fontSize: "14px"
                  }}
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleDiscover}
                  disabled={discovering}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "8px",
                    border: "none",
                    background: discovering ? "#4b5563" : "#22c55e",
                    color: "#fff",
                    cursor: discovering ? "not-allowed" : "pointer",
                    fontWeight: "bold"
                  }}
                >
                  {discovering ? "Discovering..." : "Discover"}
                </motion.button>
              </div>

              <AnimatePresence>
                {discoverError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    style={{ 
                      color: "#ef4444", 
                      marginBottom: "15px",
                      padding: "10px",
                      background: "rgba(239, 68, 68, 0.1)",
                      borderRadius: "8px",
                      border: "1px solid rgba(239, 68, 68, 0.3)"
                    }}
                  >
                    {discoverError}
                  </motion.div>
                )}
              </AnimatePresence>

              {hosts.length > 0 && (
                <div style={{
                  maxHeight: "300px",
                  overflowY: "auto",
                  borderTop: "1px solid rgba(255,255,255,0.1)",
                  marginTop: "15px",
                  paddingTop: "15px"
                }}>
                  <p style={{ marginBottom: "10px", color: "#94a3b8" }}>
                    🎯 Active devices ({hosts.length}):
                  </p>
                  <div style={{ display: "grid", gap: "8px" }}>
                    {hosts.map((h, idx) => (
                      <motion.div
                        key={`${h.ip}-${idx}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "10px",
                          background: "rgba(255,255,255,0.05)",
                          borderRadius: "8px",
                          border: "1px solid rgba(255,255,255,0.1)"
                        }}
                      >
                        <span>
                          <strong>{h.ip}</strong>{" "}
                          {h.hostname && (
                            <span style={{ color: "#94a3b8" }}>({h.hostname})</span>
                          )}
                        </span>
                        <div style={{ display: "flex", gap: "5px" }}>
                          {h.open_ports && h.open_ports.slice(0, 3).map((port) => (
                            <span
                              key={port}
                              style={{
                                padding: "2px 6px",
                                background: "#3b82f6",
                                borderRadius: "4px",
                                fontSize: "11px"
                              }}
                            >
                              {port}
                            </span>
                          ))}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === "history" && (
            <motion.div style={cardStyle}>
              <ScanHistory onSelectScan={setSelectedScan} />
            </motion.div>
          )}

          {activeTab === "results" && (
            <motion.div style={cardStyle}>
              <EnhancedScanResult result={selectedScan} />
            </motion.div>
          )}
        </motion.div>
      </AnimatePresence>
      
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
    </div>
  );
}
