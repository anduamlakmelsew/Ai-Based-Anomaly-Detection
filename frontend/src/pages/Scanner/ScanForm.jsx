import { useState } from "react";
import { startScan } from "../../services/scanService";

export default function ScanForm({ onScanComplete }) {
  const [target, setTarget] = useState("");
  const [scanType, setScanType] = useState("network");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!target) {
      setError("Target is required");
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await startScan({
        target,
        scan_type: scanType,
      });

      // 🔥 Get scan data from response
      const scan = response?.data || response?.result || null;

      if (scan) {
        // ✅ Callback to parent to update selected scan
        if (onScanComplete) onScanComplete(scan);

        setSuccess(`Scan started for target: ${scan.target || target}`);
        setTarget("");
      } else {
        console.warn("⚠️ Scan data not found in response");
        setError("Scan started but no data returned.");
      }
    } catch (err) {
      console.error(err);
      setError("Scan failed. Check backend logs.");
    }

    setLoading(false);
  };

  const getButtonStyle = (type) => ({
    padding: "8px 12px",
    marginRight: "10px",
    borderRadius: "6px",
    border: "1px solid #1f2937",
    background: scanType === type ? "#2563eb" : "#111827",
    color: "#fff",
    cursor: "pointer",
  });

  return (
    <div
      style={{
        padding: "20px",
        borderRadius: "8px",
        backgroundColor: "#111827",
        marginBottom: "20px",
      }}
    >
      <h3 style={{ marginBottom: "15px" }}>Start New Scan</h3>

      {error && <p style={{ color: "red", marginBottom: "10px" }}>{error}</p>}
      {success && (
        <p style={{ color: "green", marginBottom: "10px" }}>{success}</p>
      )}

      <form onSubmit={handleSubmit}>
        {/* TARGET INPUT */}
        <input
          type="text"
          placeholder="Enter target (IP or URL)"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          style={{
            width: "100%",
            padding: "10px",
            borderRadius: "6px",
            border: "1px solid #1f2937",
            background: "#020617",
            color: "#fff",
            marginBottom: "15px",
          }}
        />

        {/* SCAN TYPE BUTTONS */}
        <div style={{ marginBottom: "15px" }}>
          <button
            type="button"
            style={getButtonStyle("network")}
            onClick={() => setScanType("network")}
          >
            Network
          </button>
          <button
            type="button"
            style={getButtonStyle("system")}
            onClick={() => setScanType("system")}
          >
            System
          </button>
          <button
            type="button"
            style={getButtonStyle("web")}
            onClick={() => setScanType("web")}
          >
            Web
          </button>
        </div>

        {/* SUBMIT BUTTON */}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "10px",
            borderRadius: "6px",
            border: "none",
            background: loading ? "#374151" : "#16a34a",
            color: "#fff",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Scanning..." : "Start Scan"}
        </button>
      </form>
    </div>
  );
}
