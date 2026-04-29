import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import MainLayout from "../../components/layout/MainLayout";
import ModelUpload from "../../components/ModelUpload";
import { getSettingsByCategory, updateSettings } from "../../services/settingsService";

export default function AdminSettings() {
  const [activeTab, setActiveTab] = useState("scanner");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  
  // Scanner Settings
  const [scannerSettings, setScannerSettings] = useState({
    scan_timeout: 300,
    port_range_start: 1,
    port_range_end: 1000,
    enable_network_scanner: true,
    enable_web_scanner: true,
    enable_system_scanner: true,
    max_concurrent_scans: 3,
    scan_interval_minutes: 60,
  });
  
  // AI Settings
  const [aiSettings, setAiSettings] = useState({
    ai_anomaly_threshold: 0.75,
    enable_ai_analysis: true,
    enable_ai_network: true,
    enable_ai_web: true,
    enable_ai_system: true,
    active_network_model: "default",
    active_web_model: "default",
    active_system_model: "default",
  });
  
  // System Settings
  const [systemSettings, setSystemSettings] = useState({
    dashboard_refresh_interval: 30,
    retention_days: 90,
    auto_cleanup: true,
    theme: "dark",
  });

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      
      // Load scanner settings
      const scannerRes = await getSettingsByCategory("scanner");
      if (scannerRes.success) {
        setScannerSettings(prev => ({ ...prev, ...scannerRes.data }));
      }
      
      // Load AI settings
      const aiRes = await getSettingsByCategory("ai");
      if (aiRes.success) {
        setAiSettings(prev => ({ ...prev, ...aiRes.data }));
      }
      
      // Load system settings
      const systemRes = await getSettingsByCategory("system");
      if (systemRes.success) {
        setSystemSettings(prev => ({ ...prev, ...systemRes.data }));
      }
    } catch (err) {
      console.error("Failed to load settings:", err);
      setError("Failed to load some settings");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveScanner = async (e) => {
    e.preventDefault();
    await saveSettings(scannerSettings, "Scanner");
  };

  const handleSaveAI = async (e) => {
    e.preventDefault();
    await saveSettings(aiSettings, "AI");
  };

  const handleSaveSystem = async (e) => {
    e.preventDefault();
    await saveSettings(systemSettings, "System");
  };

  const saveSettings = async (settings, category) => {
    setLoading(true);
    setMessage("");
    setError("");
    
    try {
      const response = await updateSettings(settings);
      if (response.success) {
        setMessage(`${category} settings saved successfully!`);
      } else {
        setError(response.error || `Failed to save ${category} settings`);
      }
    } catch (err) {
      console.error(`Save ${category} settings error:`, err);
      setError(err.response?.data?.error || `Failed to save ${category} settings`);
    } finally {
      setLoading(false);
      setTimeout(() => {
        setMessage("");
        setError("");
      }, 3000);
    }
  };

  const cardStyle = {
    background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
    padding: "24px",
    borderRadius: "16px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1)",
    color: "#fff",
    border: "1px solid rgba(255,255,255,0.1)",
    marginBottom: "20px",
  };

  const inputStyle = {
    width: "100%",
    padding: "12px 16px",
    background: "rgba(15, 23, 42, 0.8)",
    border: "1px solid rgba(255,255,255,0.2)",
    borderRadius: "8px",
    color: "#fff",
    fontSize: "14px",
    marginTop: "8px",
  };

  const buttonStyle = {
    padding: "12px 24px",
    background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
    marginTop: "20px",
    opacity: loading ? 0.6 : 1,
  };

  const tabStyle = (isActive) => ({
    padding: "12px 24px",
    background: isActive ? "linear-gradient(135deg, #3b82f6, #8b5cf6)" : "rgba(30, 41, 59, 0.8)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
    marginRight: "10px",
    marginBottom: "10px",
  });

  const checkboxStyle = {
    width: "18px",
    height: "18px",
    cursor: "pointer",
  };

  return (
    <MainLayout>
      <div style={{ color: "#fff", paddingBottom: "50px" }}>
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h2 style={{
            marginBottom: "10px",
            fontSize: "2rem",
            fontWeight: "bold",
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}>
            ⚙️ Admin Settings
          </h2>
          <p style={{ color: "#94a3b8", marginBottom: "20px" }}>
            Configure scanner, AI models, and system preferences
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <div style={{ marginBottom: "20px" }}>
          <button onClick={() => setActiveTab("scanner")} style={tabStyle(activeTab === "scanner")}>
            🔍 Scanner Config
          </button>
          <button onClick={() => setActiveTab("ai")} style={tabStyle(activeTab === "ai")}>
            🤖 AI Models
          </button>
          <button onClick={() => setActiveTab("models")} style={tabStyle(activeTab === "models")}>
            📦 Upload Models
          </button>
          <button onClick={() => setActiveTab("system")} style={tabStyle(activeTab === "system")}>
            🖥️ System
          </button>
        </div>

        {/* Status Messages */}
        {message && (
          <div style={{ color: "#10b981", marginBottom: "10px", padding: "10px", background: "rgba(34, 197, 94, 0.1)", borderRadius: "8px" }}>
            {message}
          </div>
        )}
        {error && (
          <div style={{ color: "#ef4444", marginBottom: "10px", padding: "10px", background: "rgba(239, 68, 68, 0.1)", borderRadius: "8px" }}>
            {error}
          </div>
        )}

        {/* Scanner Settings Tab */}
        {activeTab === "scanner" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div style={cardStyle}>
              <h3 style={{ marginBottom: "20px", color: "#3b82f6" }}>🔍 Scanner Configuration</h3>
              <form onSubmit={handleSaveScanner}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                  <div style={{ marginBottom: "20px" }}>
                    <label style={{ color: "#94a3b8" }}>
                      Scan Timeout (seconds):
                      <input
                        type="number"
                        value={scannerSettings.scan_timeout}
                        onChange={(e) => setScannerSettings({ ...scannerSettings, scan_timeout: parseInt(e.target.value) })}
                        style={inputStyle}
                        min="30"
                        max="3600"
                      />
                    </label>
                  </div>
                  <div style={{ marginBottom: "20px" }}>
                    <label style={{ color: "#94a3b8" }}>
                      Max Concurrent Scans:
                      <input
                        type="number"
                        value={scannerSettings.max_concurrent_scans}
                        onChange={(e) => setScannerSettings({ ...scannerSettings, max_concurrent_scans: parseInt(e.target.value) })}
                        style={inputStyle}
                        min="1"
                        max="10"
                      />
                    </label>
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                  <div style={{ marginBottom: "20px" }}>
                    <label style={{ color: "#94a3b8" }}>
                      Port Range Start:
                      <input
                        type="number"
                        value={scannerSettings.port_range_start}
                        onChange={(e) => setScannerSettings({ ...scannerSettings, port_range_start: parseInt(e.target.value) })}
                        style={inputStyle}
                        min="1"
                        max="65535"
                      />
                    </label>
                  </div>
                  <div style={{ marginBottom: "20px" }}>
                    <label style={{ color: "#94a3b8" }}>
                      Port Range End:
                      <input
                        type="number"
                        value={scannerSettings.port_range_end}
                        onChange={(e) => setScannerSettings({ ...scannerSettings, port_range_end: parseInt(e.target.value) })}
                        style={inputStyle}
                        min="1"
                        max="65535"
                      />
                    </label>
                  </div>
                </div>

                <div style={{ marginBottom: "20px" }}>
                  <h4 style={{ color: "#cbd5e1", marginBottom: "15px" }}>Enabled Scanners</h4>
                  <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={scannerSettings.enable_network_scanner}
                        onChange={(e) => setScannerSettings({ ...scannerSettings, enable_network_scanner: e.target.checked })}
                        style={checkboxStyle}
                      />
                      Network Scanner
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={scannerSettings.enable_web_scanner}
                        onChange={(e) => setScannerSettings({ ...scannerSettings, enable_web_scanner: e.target.checked })}
                        style={checkboxStyle}
                      />
                      Web Vulnerability Scanner
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={scannerSettings.enable_system_scanner}
                        onChange={(e) => setScannerSettings({ ...scannerSettings, enable_system_scanner: e.target.checked })}
                        style={checkboxStyle}
                      />
                      System Audit Scanner
                    </label>
                  </div>
                </div>

                <motion.button 
                  whileHover={{ scale: loading ? 1 : 1.05 }} 
                  whileTap={{ scale: loading ? 1 : 0.95 }} 
                  type="submit" 
                  style={buttonStyle}
                  disabled={loading}
                >
                  {loading ? "⏳ Saving..." : "💾 Save Scanner Settings"}
                </motion.button>
              </form>
            </div>
          </motion.div>
        )}

        {/* AI Settings Tab */}
        {activeTab === "ai" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div style={cardStyle}>
              <h3 style={{ marginBottom: "20px", color: "#8b5cf6" }}>🤖 AI Model Configuration</h3>
              <form onSubmit={handleSaveAI}>
                <div style={{ marginBottom: "20px" }}>
                  <label style={{ color: "#94a3b8" }}>
                    Anomaly Threshold (0-1):
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={aiSettings.ai_anomaly_threshold}
                      onChange={(e) => setAiSettings({ ...aiSettings, ai_anomaly_threshold: parseFloat(e.target.value) })}
                      style={inputStyle}
                    />
                  </label>
                  <small style={{ color: "#64748b" }}>Higher values = stricter anomaly detection</small>
                </div>

                <div style={{ marginBottom: "20px" }}>
                  <h4 style={{ color: "#cbd5e1", marginBottom: "15px" }}>AI Analysis Per Scanner</h4>
                  <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={aiSettings.enable_ai_analysis}
                        onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_analysis: e.target.checked })}
                        style={checkboxStyle}
                      />
                      Enable AI Analysis Globally
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={aiSettings.enable_ai_network}
                        onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_network: e.target.checked })}
                        style={checkboxStyle}
                      />
                      Network Scans
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={aiSettings.enable_ai_web}
                        onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_web: e.target.checked })}
                        style={checkboxStyle}
                      />
                      Web Scans
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={aiSettings.enable_ai_system}
                        onChange={(e) => setAiSettings({ ...aiSettings, enable_ai_system: e.target.checked })}
                        style={checkboxStyle}
                      />
                      System Scans
                    </label>
                  </div>
                </div>

                <div style={{ marginBottom: "20px" }}>
                  <h4 style={{ color: "#cbd5e1", marginBottom: "15px" }}>Active Models</h4>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "15px" }}>
                    <div>
                      <label style={{ color: "#94a3b8", fontSize: "12px" }}>Network Model</label>
                      <input
                        type="text"
                        value={aiSettings.active_network_model}
                        onChange={(e) => setAiSettings({ ...aiSettings, active_network_model: e.target.value })}
                        style={inputStyle}
                        placeholder="default"
                      />
                    </div>
                    <div>
                      <label style={{ color: "#94a3b8", fontSize: "12px" }}>Web Model</label>
                      <input
                        type="text"
                        value={aiSettings.active_web_model}
                        onChange={(e) => setAiSettings({ ...aiSettings, active_web_model: e.target.value })}
                        style={inputStyle}
                        placeholder="default"
                      />
                    </div>
                    <div>
                      <label style={{ color: "#94a3b8", fontSize: "12px" }}>System Model</label>
                      <input
                        type="text"
                        value={aiSettings.active_system_model}
                        onChange={(e) => setAiSettings({ ...aiSettings, active_system_model: e.target.value })}
                        style={inputStyle}
                        placeholder="default"
                      />
                    </div>
                  </div>
                </div>

                <motion.button 
                  whileHover={{ scale: loading ? 1 : 1.05 }} 
                  whileTap={{ scale: loading ? 1 : 0.95 }} 
                  type="submit" 
                  style={buttonStyle}
                  disabled={loading}
                >
                  {loading ? "⏳ Saving..." : "💾 Save AI Settings"}
                </motion.button>
              </form>
            </div>
          </motion.div>
        )}

        {/* Model Upload Tab */}
        {activeTab === "models" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <ModelUpload onUploadSuccess={(model) => {
              setMessage(`Model ${model.model_type} v${model.version} uploaded successfully!`);
              setTimeout(() => setMessage(""), 5000);
            }} />
          </motion.div>
        )}

        {/* System Settings Tab */}
        {activeTab === "system" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div style={cardStyle}>
              <h3 style={{ marginBottom: "20px", color: "#06b6d4" }}>🖥️ System Preferences</h3>
              <form onSubmit={handleSaveSystem}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                  <div style={{ marginBottom: "20px" }}>
                    <label style={{ color: "#94a3b8" }}>
                      Dashboard Refresh (seconds):
                      <input
                        type="number"
                        value={systemSettings.dashboard_refresh_interval}
                        onChange={(e) => setSystemSettings({ ...systemSettings, dashboard_refresh_interval: parseInt(e.target.value) })}
                        style={inputStyle}
                        min="10"
                        max="300"
                      />
                    </label>
                  </div>
                  <div style={{ marginBottom: "20px" }}>
                    <label style={{ color: "#94a3b8" }}>
                      Data Retention (days):
                      <input
                        type="number"
                        value={systemSettings.retention_days}
                        onChange={(e) => setSystemSettings({ ...systemSettings, retention_days: parseInt(e.target.value) })}
                        style={inputStyle}
                        min="7"
                        max="365"
                      />
                    </label>
                  </div>
                </div>

                <div style={{ marginBottom: "20px" }}>
                  <label style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={systemSettings.auto_cleanup}
                      onChange={(e) => setSystemSettings({ ...systemSettings, auto_cleanup: e.target.checked })}
                      style={checkboxStyle}
                    />
                    Enable Automatic Data Cleanup
                  </label>
                </div>

                <motion.button 
                  whileHover={{ scale: loading ? 1 : 1.05 }} 
                  whileTap={{ scale: loading ? 1 : 0.95 }} 
                  type="submit" 
                  style={buttonStyle}
                  disabled={loading}
                >
                  {loading ? "⏳ Saving..." : "💾 Save System Settings"}
                </motion.button>
              </form>
            </div>
          </motion.div>
        )}
      </div>
    </MainLayout>
  );
}
