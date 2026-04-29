import { useState } from "react";
import { 
  runAIManualTest, 
  getNetworkTemplate, 
  getSystemTemplate, 
  getWebTemplate 
} from "../../services/aiService";

/**
 * AI Security Lab - Manual AI Testing Interface
 * Allows users to test the AI models with custom inputs
 */
export default function AISecurityLab() {
  const [activeTab, setActiveTab] = useState("unified");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Input states
  const [networkData, setNetworkData] = useState(getNetworkTemplate());
  const [systemData, setSystemData] = useState(getSystemTemplate());
  const [webData, setWebData] = useState(getWebTemplate());

  const handleRunTest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {};
      
      if (activeTab === "unified" || activeTab === "network") {
        payload.network = networkData;
      }
      if (activeTab === "unified" || activeTab === "system") {
        payload.system = systemData;
      }
      if (activeTab === "unified" || activeTab === "web") {
        payload.web = webData;
      }

      const response = await runAIManualTest(payload);
      
      if (response.success) {
        setResult(response.data);
      } else {
        setError(response.error || "Test failed");
      }
    } catch (err) {
      setError(err.message || "Failed to run AI test");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = (type) => {
    if (type === "network") setNetworkData(getNetworkTemplate());
    if (type === "system") setSystemData(getSystemTemplate());
    if (type === "web") setWebData(getWebTemplate());
  };

  const getRiskColor = (level) => {
    switch (level?.toUpperCase()) {
      case "CRITICAL": return "#ef4444";
      case "HIGH": return "#f97316";
      case "MEDIUM": return "#eab308";
      case "LOW": return "#22c55e";
      default: return "#6b7280";
    }
  };

  const cardStyle = {
    background: "#1e293b",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
    color: "#fff",
    marginBottom: "20px"
  };

  const inputStyle = {
    width: "100%",
    padding: "10px",
    borderRadius: "6px",
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#fff",
    fontSize: "14px",
    marginBottom: "10px"
  };

  const labelStyle = {
    display: "block",
    marginBottom: "5px",
    color: "#94a3b8",
    fontSize: "12px",
    textTransform: "uppercase"
  };

  const buttonStyle = {
    padding: "12px 24px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "14px",
    transition: "all 0.2s"
  };

  const tabStyle = (isActive) => ({
    padding: "10px 20px",
    borderRadius: "6px",
    border: "none",
    cursor: "pointer",
    background: isActive ? "#3b82f6" : "#334155",
    color: "#fff",
    fontWeight: isActive ? "600" : "400",
    marginRight: "10px"
  });

  const renderNetworkForm = () => (
    <div style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
        <h3>🌐 Network Data</h3>
        <button 
          onClick={() => handleReset("network")}
          style={{ ...buttonStyle, background: "#64748b", padding: "6px 12px", fontSize: "12px" }}
        >
          Reset
        </button>
      </div>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
        <div>
          <label style={labelStyle}>Duration (seconds)</label>
          <input
            type="number"
            step="0.1"
            style={inputStyle}
            value={networkData.duration}
            onChange={(e) => setNetworkData({...networkData, duration: parseFloat(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Source Bytes</label>
          <input
            type="number"
            style={inputStyle}
            value={networkData.src_bytes}
            onChange={(e) => setNetworkData({...networkData, src_bytes: parseInt(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Destination Bytes</label>
          <input
            type="number"
            style={inputStyle}
            value={networkData.dst_bytes}
            onChange={(e) => setNetworkData({...networkData, dst_bytes: parseInt(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Protocol</label>
          <select
            style={inputStyle}
            value={networkData.protocol}
            onChange={(e) => setNetworkData({...networkData, protocol: e.target.value})}
          >
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
            <option value="icmp">ICMP</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>Packet Count</label>
          <input
            type="number"
            style={inputStyle}
            value={networkData.packet_count}
            onChange={(e) => setNetworkData({...networkData, packet_count: parseInt(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Destination Port</label>
          <input
            type="number"
            style={inputStyle}
            value={networkData.dst_port}
            onChange={(e) => setNetworkData({...networkData, dst_port: parseInt(e.target.value)})}
          />
        </div>
      </div>

      <div style={{ marginTop: "15px", display: "flex", gap: "10px" }}>
        {["syn_flag", "ack_flag", "rst_flag", "fin_flag"].map((flag) => (
          <label key={flag} style={{ display: "flex", alignItems: "center", gap: "5px", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={networkData[flag] === 1}
              onChange={(e) => setNetworkData({...networkData, [flag]: e.target.checked ? 1 : 0})}
            />
            <span style={{ fontSize: "12px", textTransform: "uppercase" }}>{flag.replace("_flag", "")}</span>
          </label>
        ))}
      </div>
    </div>
  );

  const renderSystemForm = () => (
    <div style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
        <h3>🔧 System Data</h3>
        <button 
          onClick={() => handleReset("system")}
          style={{ ...buttonStyle, background: "#64748b", padding: "6px 12px", fontSize: "12px" }}
        >
          Reset
        </button>
      </div>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "15px" }}>
        <div>
          <label style={labelStyle}>CPU Usage (%)</label>
          <input
            type="number"
            min="0"
            max="100"
            style={inputStyle}
            value={systemData.cpu_usage}
            onChange={(e) => setSystemData({...systemData, cpu_usage: parseFloat(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Memory Usage (%)</label>
          <input
            type="number"
            min="0"
            max="100"
            style={inputStyle}
            value={systemData.memory_usage}
            onChange={(e) => setSystemData({...systemData, memory_usage: parseFloat(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Disk Usage (%)</label>
          <input
            type="number"
            min="0"
            max="100"
            style={inputStyle}
            value={systemData.disk_usage}
            onChange={(e) => setSystemData({...systemData, disk_usage: parseFloat(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Open Ports</label>
          <input
            type="number"
            style={inputStyle}
            value={systemData.open_ports}
            onChange={(e) => setSystemData({...systemData, open_ports: parseInt(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Process Count</label>
          <input
            type="number"
            style={inputStyle}
            value={systemData.process_count}
            onChange={(e) => setSystemData({...systemData, process_count: parseInt(e.target.value)})}
          />
        </div>
        <div>
          <label style={labelStyle}>Suspicious Processes</label>
          <input
            type="number"
            style={inputStyle}
            value={systemData.suspicious_processes}
            onChange={(e) => setSystemData({...systemData, suspicious_processes: parseInt(e.target.value)})}
          />
        </div>
      </div>
    </div>
  );

  const renderWebForm = () => (
    <div style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
        <h3>🌍 Web Data</h3>
        <button 
          onClick={() => handleReset("web")}
          style={{ ...buttonStyle, background: "#64748b", padding: "6px 12px", fontSize: "12px" }}
        >
          Reset
        </button>
      </div>
      
      <div>
        <label style={labelStyle}>URL</label>
        <input
          type="text"
          style={inputStyle}
          value={webData.url}
          onChange={(e) => setWebData({...webData, url: e.target.value})}
        />
      </div>
      
      <div>
        <label style={labelStyle}>Method</label>
        <select
          style={inputStyle}
          value={webData.method}
          onChange={(e) => setWebData({...webData, method: e.target.value})}
        >
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
        </select>
      </div>
      
      <div>
        <label style={labelStyle}>Payload (for vulnerability detection)</label>
        <textarea
          style={{ ...inputStyle, minHeight: "100px", fontFamily: "monospace" }}
          value={webData.payload}
          onChange={(e) => setWebData({...webData, payload: e.target.value})}
          placeholder="Enter payload text or HTTP response content..."
        />
      </div>
    </div>
  );

  const renderResult = () => {
    if (!result) return null;

    const globalRisk = result.global_status || "UNKNOWN";
    const riskScore = result.global_risk_score || 0;
    const degraded = result.degraded_mode || false;

    return (
      <div style={{ ...cardStyle, borderLeft: `4px solid ${getRiskColor(globalRisk)}` }}>
        <h3>🎯 AI Analysis Result</h3>
        
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "20px", marginBottom: "20px" }}>
          <div style={{ textAlign: "center", padding: "15px", background: "#0f172a", borderRadius: "8px" }}>
            <div style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "5px" }}>RISK LEVEL</div>
            <div style={{ fontSize: "24px", fontWeight: "bold", color: getRiskColor(globalRisk) }}>
              {globalRisk}
            </div>
          </div>
          <div style={{ textAlign: "center", padding: "15px", background: "#0f172a", borderRadius: "8px" }}>
            <div style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "5px" }}>RISK SCORE</div>
            <div style={{ fontSize: "24px", fontWeight: "bold", color: "#fff" }}>
              {riskScore.toFixed(1)}
            </div>
          </div>
          <div style={{ textAlign: "center", padding: "15px", background: "#0f172a", borderRadius: "8px" }}>
            <div style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "5px" }}>MODE</div>
            <div style={{ fontSize: "24px", fontWeight: "bold", color: degraded ? "#f59e0b" : "#22c55e" }}>
              {degraded ? "DEGRADED" : "NORMAL"}
            </div>
          </div>
        </div>

        {/* Individual Predictions */}
        {result.network && (
          <div style={{ marginBottom: "15px", padding: "15px", background: "#0f172a", borderRadius: "8px" }}>
            <h4 style={{ marginBottom: "10px", color: "#3b82f6" }}>🌐 Network Analysis</h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              <div>Attack: <span style={{ color: result.network.is_attack ? "#ef4444" : "#22c55e" }}>
                {result.network.is_attack ? "YES" : "NO"}
              </span></div>
              <div>Category: {result.network.attack_category}</div>
              <div>Probability: {(result.network.attack_probability * 100).toFixed(1)}%</div>
              <div>Risk: {result.network.risk_level}</div>
            </div>
          </div>
        )}

        {result.system && (
          <div style={{ marginBottom: "15px", padding: "15px", background: "#0f172a", borderRadius: "8px" }}>
            <h4 style={{ marginBottom: "10px", color: "#22c55e" }}>🔧 System Analysis</h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              <div>Risk Level: {result.system.risk_level}</div>
              <div>Risk Score: {result.system.risk_score?.toFixed(1)}</div>
              <div>Anomaly: {(result.system.anomaly_score * 100).toFixed(1)}%</div>
            </div>
          </div>
        )}

        {result.web && (
          <div style={{ marginBottom: "15px", padding: "15px", background: "#0f172a", borderRadius: "8px" }}>
            <h4 style={{ marginBottom: "10px", color: "#f59e0b" }}>🌍 Web Analysis</h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              <div>Vulnerable: <span style={{ color: result.web.is_vulnerable ? "#ef4444" : "#22c55e" }}>
                {result.web.is_vulnerable ? "YES" : "NO"}
              </span></div>
              <div>Type: {result.web.vulnerability_type}</div>
              <div>Confidence: {(result.web.confidence * 100).toFixed(1)}%</div>
              <div>Severity: {result.web.severity}</div>
            </div>
          </div>
        )}

        {/* Missing Inputs */}
        {result.missing_inputs && Object.keys(result.missing_inputs).length > 0 && (
          <div style={{ marginTop: "15px", padding: "10px", background: "#451a1a", borderRadius: "6px" }}>
            <h4 style={{ color: "#fca5a5", marginBottom: "5px" }}>⚠️ Missing Inputs</h4>
            <pre style={{ fontSize: "12px", overflow: "auto" }}>
              {JSON.stringify(result.missing_inputs, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ color: "#fff", paddingBottom: "50px" }}>
      <h2 style={{ marginBottom: "20px" }}>🧪 AI Security Lab</h2>
      <p style={{ color: "#94a3b8", marginBottom: "20px" }}>
        Test the AI models with custom inputs. Enter network, system, and web data to analyze security risks.
      </p>

      {/* Tabs */}
      <div style={{ marginBottom: "20px" }}>
        <button 
          style={tabStyle(activeTab === "unified")} 
          onClick={() => setActiveTab("unified")}
        >
          🧪 Unified Test
        </button>
        <button 
          style={tabStyle(activeTab === "network")} 
          onClick={() => setActiveTab("network")}
        >
          🌐 Network
        </button>
        <button 
          style={tabStyle(activeTab === "system")} 
          onClick={() => setActiveTab("system")}
        >
          🔧 System
        </button>
        <button 
          style={tabStyle(activeTab === "web")} 
          onClick={() => setActiveTab("web")}
        >
          🌍 Web
        </button>
      </div>

      {/* Input Forms */}
      {(activeTab === "unified" || activeTab === "network") && renderNetworkForm()}
      {(activeTab === "unified" || activeTab === "system") && renderSystemForm()}
      {(activeTab === "unified" || activeTab === "web") && renderWebForm()}

      {/* Action Buttons */}
      <div style={{ display: "flex", gap: "15px", marginBottom: "20px" }}>
        <button
          onClick={handleRunTest}
          disabled={loading}
          style={{
            ...buttonStyle,
            background: loading ? "#475569" : "#3b82f6",
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? "⏳ Running Analysis..." : "🚀 Run AI Analysis"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div style={{ ...cardStyle, background: "#451a1a", border: "1px solid #ef4444" }}>
          <h3>❌ Error</h3>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {/* Results */}
      {renderResult()}
    </div>
  );
}
