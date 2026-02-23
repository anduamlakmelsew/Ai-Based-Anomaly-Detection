// src/pages/Reports/ReportGenerator.jsx

import { useState } from "react";
import Table from "../../components/common/Table";

function ReportGenerator() {
  // Sample report data
  const [reports] = useState([
    {
      date: "2026-02-22",
      type: "Full System Scan",
      target: "192.168.1.10",
      status: "Generated",
    },
    {
      date: "2026-02-21",
      type: "Web Vulnerability Scan",
      target: "example.com",
      status: "Generated",
    },
    {
      date: "2026-02-20",
      type: "Network Scan",
      target: "10.0.0.5",
      status: "Generated",
    },
  ]);

  const columns = ["Date", "Type", "Target", "Status", "Action"];

  // Map reports to table data with a Download button
  const tableData = reports.map((report) => ({
    ...report,
    Action: (
      <button
        style={{
          padding: "5px 10px",
          backgroundColor: "#16a34a",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        Download
      </button>
    ),
  }));

  return (
    <div style={{ padding: "20px" }}>
      <h2>Reports Module</h2>

      {/* Summary Cards */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "20px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            backgroundColor: "#2563eb",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            minWidth: "150px",
            textAlign: "center",
          }}
        >
          <h3>Total Reports</h3>
          <p style={{ fontSize: "24px", margin: "10px 0" }}>{reports.length}</p>
        </div>

        <div
          style={{
            backgroundColor: "#16a34a",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            minWidth: "150px",
            textAlign: "center",
          }}
        >
          <h3>Last Generated</h3>
          <p style={{ fontSize: "24px", margin: "10px 0" }}>
            {reports[0].date}
          </p>
        </div>
      </div>

      {/* Reports Table */}
      <div style={{ marginTop: "40px" }}>
        <h3>Report History</h3>
        <Table columns={columns} data={tableData} />
      </div>
    </div>
  );
}

export default ReportGenerator;
