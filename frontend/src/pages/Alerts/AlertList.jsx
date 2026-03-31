// src/pages/Alerts/AlertList.jsx
import { useEffect, useState } from "react";
import Table from "../../components/common/Table";
import Modal from "../../components/common/Modal";
import { getAlerts } from "../../services/alertService";

export default function AlertList() {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await getAlerts();
        if (isMounted) setAlerts(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error("Failed to load alerts:", e);
        if (isMounted) setError("Failed to load alerts.");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    load();
    return () => {
      isMounted = false;
    };
  }, []);

  const columns = ["Time", "Message", "Severity", "Status", "Action"];

  const tableData = alerts.map((alert) => {
    const sev = String(alert.severity || "").toUpperCase();
    const isCritical = sev === "CRITICAL" || sev === "HIGH";

    return {
      Time: new Date(alert.created_at).toLocaleString(),
      Message: alert.message,
      Severity: (
        <span
          style={{
            padding: "4px 10px",
            borderRadius: "999px",
            backgroundColor: isCritical ? "#b91c1c" : "#f59e0b",
            color: "#fff",
            fontWeight: "bold",
            fontSize: "12px",
          }}
        >
          {isCritical ? "High Priority" : sev || "INFO"}
        </span>
      ),
      Status: alert.status || "open",
      Action: (
        <button
          onClick={() => setSelectedAlert(alert)}
          style={{
            padding: "6px 12px",
            backgroundColor: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            transition: "0.2s",
          }}
          onMouseEnter={(e) => (e.target.style.backgroundColor = "#1e40af")}
          onMouseLeave={(e) => (e.target.style.backgroundColor = "#2563eb")}
        >
          View
        </button>
      ),
    };
  });

  const cardStyle = {
    background: "#1e293b",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
    color: "#fff",
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2 style={{ marginBottom: "20px" }}>🚨 Alerts Module</h2>

      <div style={cardStyle}>
        {loading && <p>Loading alerts...</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}
        {!loading && !error && alerts.length === 0 && <p>No alerts.</p>}
        {!loading && !error && alerts.length > 0 && (
          <Table columns={columns} data={tableData} />
        )}
      </div>

      {selectedAlert && (
        <Modal onClose={() => setSelectedAlert(null)}>
          <div style={{ padding: "15px", color: "#fff" }}>
            <h3>Alert Details</h3>
            <p>
              <strong>Time:</strong>{" "}
              {new Date(selectedAlert.created_at).toLocaleString()}
            </p>
            <p>
              <strong>Severity:</strong>{" "}
              {String(selectedAlert.severity || "").toUpperCase()}
            </p>
            <p>
              <strong>Status:</strong> {selectedAlert.status || "open"}
            </p>
            <p>
              <strong>Message:</strong> {selectedAlert.message}
            </p>
          </div>
        </Modal>
      )}
    </div>
  );
}
