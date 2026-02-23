// src/pages/Alerts/AlertList.jsx
import { useState } from "react";
import Table from "../../components/common/Table";
import Modal from "../../components/common/Modal";

function AlertList() {
  // Sample alert data
  const [alerts] = useState([
    {
      Time: "2026-02-20 10:15",
      Source: "192.168.1.10",
      Type: "System",
      Severity: "Critical",
      Description: "Unauthorized login attempt",
    },
    {
      Time: "2026-02-20 09:50",
      Source: "example.com",
      Type: "Web",
      Severity: "Medium",
      Description: "SQL Injection attempt",
    },
    {
      Time: "2026-02-19 18:30",
      Source: "192.168.1.15",
      Type: "Network",
      Severity: "High",
      Description: "Port scan detected",
    },
  ]);

  const [selectedAlert, setSelectedAlert] = useState(null);

  const columns = ["Time", "Source", "Type", "Severity", "Action"];

  // Map alerts for the table
  const tableData = alerts.map((alert) => ({
    Time: alert.Time,
    Source: alert.Source,
    Type: alert.Type,
    Severity: alert.Severity,
    Action: (
      <button
        onClick={() => setSelectedAlert(alert)}
        style={{
          padding: "5px 10px",
          backgroundColor: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        View
      </button>
    ),
  }));

  return (
    <div style={{ padding: "20px" }}>
      <h2>Alerts Module</h2>

      {/* Table */}
      <Table columns={columns} data={tableData} />

      {/* Modal for selected alert */}
      {selectedAlert && (
        <Modal onClose={() => setSelectedAlert(null)}>
          <h3>Alert Details</h3>
          <p>
            <strong>Time:</strong> {selectedAlert.Time}
          </p>
          <p>
            <strong>Source:</strong> {selectedAlert.Source}
          </p>
          <p>
            <strong>Type:</strong> {selectedAlert.Type}
          </p>
          <p>
            <strong>Severity:</strong> {selectedAlert.Severity}
          </p>
          <p>
            <strong>Description:</strong> {selectedAlert.Description}
          </p>
        </Modal>
      )}
    </div>
  );
}

export default AlertList;
