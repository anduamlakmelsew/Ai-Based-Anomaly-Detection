import { useEffect, useState } from "react";
import { io } from "socket.io-client";
import ScanForm from "./ScanForm";
import ScanHistory from "./ScanHistory";
import ScanResult from "./ScanResult";
import { discoverHosts } from "../../services/scanService";
import { getToken } from "../../services/authService";

// 🔴 Safe socket initialization
// Socket connection with fallback
let socket = null;
let socketConnected = false;

try {
  socket = io("http://127.0.0.1:5003", {
    transports: ["websocket", "polling"],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 3
  });
  
  socket.on("connect", () => {
    console.log("✅ WebSocket connected");
    socketConnected = true;
  });
  
  socket.on("disconnect", () => {
    console.warn("⚠️ WebSocket disconnected");
    socketConnected = false;
  });
  
  socket.on("connect_error", (error) => {
    console.warn("⚠️ WebSocket connection failed, using HTTP polling fallback:", error.message);
    socketConnected = false;
  });
} catch (err) {
  console.warn("⚠️ WebSocket initialization failed, using HTTP polling fallback:", err);
  socket = null;
}

export default function ScannerPage() {
  const [selectedScan, setSelectedScan] = useState(null);
  const [liveScan, setLiveScan] = useState(null);
  const [range, setRange] = useState("192.168.1.0/24");
  const [discovering, setDiscovering] = useState(false);
  const [discoverError, setDiscoverError] = useState("");
  const [hosts, setHosts] = useState([]);

  useEffect(() => {
    if (!socket) return;

    const onProgress = (data) => {
      setLiveScan(data);
    };

    socket.on("scan_progress", onProgress);

    return () => {
      socket.off("scan_progress", onProgress);
    };
  }, []);

  const handleDiscover = async () => {
    if (!range) {
      setDiscoverError("IP range is required");
      return;
    }

    // Check authentication first
    if (!getToken()) {
      setDiscoverError("Please login first to use network discovery");
      return;
    }

    setDiscoverError("");
    setDiscovering(true);

    try {
      const data = await discoverHosts(range);
      if (!data?.success) {
        setDiscoverError(data?.error || "Discovery failed");
        setHosts([]);
      } else {
        setHosts(data.hosts || []);
      }
    } catch (e) {
      console.error("Discovery error:", e);
      setDiscoverError("Discovery failed. Check backend logs.");
      setHosts([]);
    } finally {
      setDiscovering(false);
    }
  };

  return (
    <div style={{ display: "flex", gap: "20px", color: "#fff" }}>
      {/* LEFT PANEL: Form + History */}
      <div style={{ flex: 1 }}>
        <ScanForm onScanComplete={setSelectedScan} />

        {/* NETWORK DISCOVERY */}
        <div
          style={{
            marginTop: "20px",
            background: "#020617",
            padding: "15px",
            borderRadius: "10px",
            border: "1px solid #1f2937",
          }}
        >
          <h4 style={{ marginTop: 0, marginBottom: "10px" }}>🌐 Network Discovery</h4>
          <p style={{ margin: "0 0 8px", fontSize: "13px", color: "#9ca3af" }}>
            Enter an IP range (CIDR) to find active devices before running a scan.
          </p>

          <div style={{ display: "flex", gap: "8px", marginBottom: "10px" }}>
            <input
              type="text"
              value={range}
              onChange={(e) => setRange(e.target.value)}
              placeholder="e.g. 192.168.1.0/24"
              style={{
                flex: 1,
                padding: "8px 10px",
                borderRadius: "6px",
                border: "1px solid #1f2937",
                background: "#0b1120",
                color: "#e5e7eb",
              }}
            />
            <button
              type="button"
              onClick={handleDiscover}
              disabled={discovering}
              style={{
                padding: "8px 12px",
                borderRadius: "6px",
                border: "none",
                background: discovering ? "#4b5563" : "#22c55e",
                color: "#fff",
                cursor: discovering ? "not-allowed" : "pointer",
              }}
            >
              {discovering ? "Discovering..." : "Discover"}
            </button>
          </div>

          {discoverError && (
            <p style={{ color: "red", marginBottom: "8px" }}>{discoverError}</p>
          )}

          {hosts.length > 0 && (
            <div
              style={{
                maxHeight: "180px",
                overflowY: "auto",
                borderTop: "1px solid #1f2937",
                marginTop: "8px",
                paddingTop: "8px",
                fontSize: "13px",
              }}
            >
              <p style={{ marginBottom: "6px", color: "#9ca3af" }}>
                Active devices ({hosts.length}):
              </p>
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {hosts.map((h, idx) => (
                  <li
                    key={`${h.ip}-${idx}`}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "4px 0",
                      borderBottom: "1px solid #111827",
                    }}
                  >
                    <span>
                      <strong>{h.ip}</strong>{" "}
                      {h.hostname && (
                        <span style={{ color: "#9ca3af" }}>({h.hostname})</span>
                      )}
                    </span>
                    {/* The ScanForm reads target from its own state;
                        you can copy/paste this IP into the target field
                        and then start a vulnerability scan. */}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {liveScan && liveScan.status !== "completed" && liveScan.status !== "failed" && liveScan.status !== "cancelled" && (
          <div
            style={{
              marginTop: "20px",
              background: "#111827",
              padding: "15px",
              borderRadius: "10px",
              border: "1px solid #1f2937",
            }}
          >
            <h4 style={{ marginTop: 0, marginBottom: "10px" }}>⚡ Live Scan</h4>
            <p style={{ margin: "6px 0" }}>
              <b>Target:</b> {liveScan.target || "N/A"}
            </p>
            <p style={{ margin: "6px 0" }}>
              <b>Status:</b> {liveScan.status || "N/A"}
            </p>
            <p style={{ margin: "6px 0" }}>
              <b>Stage:</b> {liveScan.stage || ""}
            </p>

            <div
              style={{
                height: "12px",
                background: "#020617",
                borderRadius: "6px",
                overflow: "hidden",
                margin: "12px 0 8px",
              }}
            >
              <div
                style={{
                  width: `${liveScan.progress || 0}%`,
                  height: "100%",
                  background: liveScan.status === "completed" ? "#22c55e" : "#3b82f6",
                  transition: "width 0.2s ease",
                }}
              />
            </div>
            <p style={{ margin: 0 }}>{liveScan.progress || 0}%</p>
          </div>
        )}

        <div style={{ marginTop: "20px" }}>
          <ScanHistory onSelectScan={setSelectedScan} />
        </div>
      </div>

      {/* RIGHT PANEL: Scan Result */}
      <div style={{ flex: 2 }}>
        <ScanResult result={selectedScan} />
      </div>
    </div>
  );
}
