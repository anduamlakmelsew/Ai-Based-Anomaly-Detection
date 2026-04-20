import { useState } from "react";
import { startScan } from "../../services/scanService";
import { getToken } from "../../services/authService";

export default function ScanForm({ onScanComplete }) {
  const [target, setTarget] = useState("");
  const [scanType, setScanType] = useState("network");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!getToken()) {
      setError("Please login to start a scan");
      return;
    }

    if (!target || !scanType) {
      setError("Target and scan type are required");
      return;
    }

    setLoading(true);

    try {
      const data = await startScan({ target, scan_type: scanType });
      onScanComplete?.(data);
      setTarget("");
      setScanType("network");
      setSuccess("Scan started successfully!");
    } catch (err) {
      console.error("Scan error:", err);
      // Don't show auth errors as they're handled by interceptor
      if (err.response?.status !== 401) {
        const message =
          err.response?.data?.error || "Scan failed. Please try again.";
        setError(message);
      }
    } finally {
      setLoading(false);
    }
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
