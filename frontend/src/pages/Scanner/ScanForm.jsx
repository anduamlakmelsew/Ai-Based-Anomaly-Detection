import { useState } from "react";
import Table from "../../components/common/Table";

function Scanner() {
  const [target, setTarget] = useState("");
  const [scanType, setScanType] = useState("System");
  const [scanResults, setScanResults] = useState([]);

  const columns = ["Time", "Target", "Scan Type", "Status"];

  // Dummy scan function (later connect to backend)
  const handleScan = () => {
    if (!target) return alert("Please enter a target IP or Domain");

    const newResult = {
      Time: new Date().toISOString().slice(0, 19).replace("T", " "),
      Target: target,
      "Scan Type": scanType,
      Status: "Completed",
    };

    setScanResults([newResult, ...scanResults]);
    setTarget("");
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Scanner Module</h2>

      {/* Scan Form */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          marginTop: "20px",
          flexWrap: "wrap",
        }}
      >
        <input
          type="text"
          placeholder="Enter target IP or Domain"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          style={{
            padding: "10px",
            flex: "1 1 200px",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        />

        <select
          value={scanType}
          onChange={(e) => setScanType(e.target.value)}
          style={{
            padding: "10px",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        >
          <option value="System">System</option>
          <option value="Web">Web</option>
          <option value="Network">Network</option>
        </select>

        <button
          onClick={handleScan}
          style={{
            padding: "10px 20px",
            borderRadius: "5px",
            border: "none",
            backgroundColor: "#2563eb",
            color: "white",
            cursor: "pointer",
          }}
        >
          Scan
        </button>
      </div>

      {/* Scan Results Table */}
      {scanResults.length > 0 && (
        <div style={{ marginTop: "40px" }}>
          <h3>Scan Results</h3>
          <Table columns={columns} data={scanResults} />
        </div>
      )}
    </div>
  );
}

export default Scanner;
