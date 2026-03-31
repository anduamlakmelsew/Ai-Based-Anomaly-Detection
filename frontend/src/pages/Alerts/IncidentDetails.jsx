import { useLocation, useNavigate } from "react-router-dom";

function IncidentDetails() {
  const location = useLocation();
  const navigate = useNavigate();
  const { alert } = location.state || {};

  if (!alert) {
    return (
      <div style={{ padding: "20px" }}>
        <h3>No alert selected</h3>
        <button onClick={() => navigate("/alerts")}>Back to Alerts</button>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Alert Details</h2>
      <p>
        <strong>Time:</strong> {alert.Time}
      </p>
      <p>
        <strong>Source:</strong> {alert.Source}
      </p>
      <p>
        <strong>Type:</strong> {alert.Type}
      </p>
      <p>
        <strong>Severity:</strong>{" "}
        <span
          style={{
            color:
              alert.Severity === "Critical"
                ? "red"
                : alert.Severity === "High"
                  ? "orange"
                  : "green",
            fontWeight: "bold",
          }}
        >
          {alert.Severity}
        </span>
      </p>
      <p>
        <strong>Description:</strong> {alert.Description}
      </p>

      {/* AI-Based Enhancement Placeholder */}
      <div
        style={{ marginTop: "20px", padding: "10px", border: "1px solid #ccc" }}
      >
        <h4>AI Recommendation:</h4>
        <p>
          Based on historical data, this type of alert is likely to escalate.
          Consider immediate review.
        </p>
      </div>

      <button
        onClick={() => navigate("/alerts")}
        style={{
          marginTop: "20px",
          padding: "5px 15px",
          backgroundColor: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        Back to Alerts
      </button>
    </div>
  );
}

export default IncidentDetails;
