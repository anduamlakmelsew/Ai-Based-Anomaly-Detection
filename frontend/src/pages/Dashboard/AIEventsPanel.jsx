import { useEffect, useState } from "react";
import { getAIDetectionStats, getAIDetectionHistory } from "../../services/aiService";

/**
 * AI Events Panel - Displays AI detection events on the dashboard
 */
export default function AIEventsPanel() {
  const [stats, setStats] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAIData();
    // Removed automatic refresh - data updates via WebSocket events or manual refresh
  }, []);

  const loadAIData = async () => {
    try {
      setLoading(true);
      
      // Load stats and recent events in parallel
      const [statsRes, eventsRes] = await Promise.all([
        getAIDetectionStats(24),
        getAIDetectionHistory(10)
      ]);
      
      if (statsRes.success) {
        setStats(statsRes.data.stats);
      }
      
      if (eventsRes.success) {
        setRecentEvents(eventsRes.data);
      }
    } catch (err) {
      console.error("Failed to load AI data:", err);
    } finally {
      setLoading(false);
    }
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
    padding: "15px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
    color: "#fff",
    marginBottom: "20px"
  };

  const badgeStyle = (level) => ({
    display: "inline-block",
    padding: "4px 8px",
    borderRadius: "4px",
    fontSize: "11px",
    fontWeight: "600",
    textTransform: "uppercase",
    background: getRiskColor(level) + "33",
    color: getRiskColor(level),
    border: `1px solid ${getRiskColor(level)}`
  });

  if (loading) {
    return (
      <div style={cardStyle}>
        <h4>🧠 AI Detection Events</h4>
        <p style={{ color: "#64748b" }}>Loading...</p>
      </div>
    );
  }

  return (
    <div style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
        <h4 style={{ margin: 0 }}>🧠 AI Detection Events (24h)</h4>
        <a href="/ai-lab" style={{ color: "#3b82f6", fontSize: "12px", textDecoration: "none" }}>
          Open AI Lab →
        </a>
      </div>

      {/* Stats Row */}
      {stats && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "10px", marginBottom: "15px" }}>
          <div style={{ textAlign: "center", padding: "10px", background: "#0f172a", borderRadius: "8px" }}>
            <div style={{ fontSize: "20px", fontWeight: "bold", color: "#ef4444" }}>
              {stats.critical}
            </div>
            <div style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase" }}>Critical</div>
          </div>
          <div style={{ textAlign: "center", padding: "10px", background: "#0f172a", borderRadius: "8px" }}>
            <div style={{ fontSize: "20px", fontWeight: "bold", color: "#f97316" }}>
              {stats.high}
            </div>
            <div style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase" }}>High</div>
          </div>
          <div style={{ textAlign: "center", padding: "10px", background: "#0f172a", borderRadius: "8px" }}>
            <div style={{ fontSize: "20px", fontWeight: "bold", color: "#eab308" }}>
              {stats.medium}
            </div>
            <div style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase" }}>Medium</div>
          </div>
          <div style={{ textAlign: "center", padding: "10px", background: "#0f172a", borderRadius: "8px" }}>
            <div style={{ fontSize: "20px", fontWeight: "bold", color: "#22c55e" }}>
              {stats.total}
            </div>
            <div style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase" }}>Total</div>
          </div>
        </div>
      )}

      {/* Recent Events Table */}
      <div style={{ maxHeight: "250px", overflow: "auto" }}>
        <table style={{ width: "100%", fontSize: "12px", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #334155" }}>
              <th style={{ textAlign: "left", padding: "8px 5px", color: "#94a3b8" }}>Time</th>
              <th style={{ textAlign: "left", padding: "8px 5px", color: "#94a3b8" }}>Source</th>
              <th style={{ textAlign: "left", padding: "8px 5px", color: "#94a3b8" }}>Target</th>
              <th style={{ textAlign: "left", padding: "8px 5px", color: "#94a3b8" }}>Risk</th>
              <th style={{ textAlign: "left", padding: "8px 5px", color: "#94a3b8" }}>Type</th>
            </tr>
          </thead>
          <tbody>
            {recentEvents.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: "center", padding: "20px", color: "#64748b" }}>
                  No AI detection events yet
                </td>
              </tr>
            ) : (
              recentEvents.map((event) => (
                <tr key={event.id} style={{ borderBottom: "1px solid #334155" }}>
                  <td style={{ padding: "8px 5px", color: "#94a3b8" }}>
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </td>
                  <td style={{ padding: "8px 5px" }}>
                    <span style={{ textTransform: "uppercase", fontSize: "10px", color: "#64748b" }}>
                      {event.source}
                    </span>
                  </td>
                  <td style={{ padding: "8px 5px", maxWidth: "120px", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {event.target}
                  </td>
                  <td style={{ padding: "8px 5px" }}>
                    <span style={badgeStyle(event.risk_level)}>
                      {event.risk_level}
                    </span>
                  </td>
                  <td style={{ padding: "8px 5px", fontSize: "11px" }}>
                    {event.attack_type}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* By Source Stats */}
      {stats?.by_source && (
        <div style={{ marginTop: "15px", paddingTop: "15px", borderTop: "1px solid #334155" }}>
          <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "8px", textTransform: "uppercase" }}>
            Events by Source
          </div>
          <div style={{ display: "flex", gap: "15px" }}>
            {Object.entries(stats.by_source).map(([source, count]) => (
              <div key={source} style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <span style={{ 
                  fontSize: "11px", 
                  color: count > 0 ? "#fff" : "#64748b",
                  fontWeight: count > 0 ? "600" : "400"
                }}>
                  {count}
                </span>
                <span style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase" }}>
                  {source}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
