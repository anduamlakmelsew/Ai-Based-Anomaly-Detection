import React, { useEffect, useMemo, useState } from "react";
import { getScanById } from "../../services/scanService";

const severityColors = {
  CRITICAL: "#dc2626",
  HIGH: "#f59e0b",
  MEDIUM: "#facc15",
  LOW: "#16a34a",
  INFO: "#3b82f6",
};

const ScanResult = ({ result }) => {
  const [scanDetails, setScanDetails] = useState(result || null);
  const scanId = result?.scan_id ?? result?.id;

  // Always prefer DB-backed results when an id is available.
  useEffect(() => {
    let isMounted = true;

    const loadFromDb = async () => {
      if (!scanId) return;
      try {
        const res = await getScanById(scanId);
        const data = res?.data || res?.result || res;
        if (isMounted) setScanDetails(data);
      } catch (e) {
        // Fall back to the passed-in result.
        console.error("Failed to fetch scan details:", e);
      }
    };

    loadFromDb();
    return () => {
      isMounted = false;
    };
  }, [scanId]);

  useEffect(() => {
    setScanDetails(result || null);
  }, [result]);

  const {
    target,
    scan_type,
    risk = { score: 0, level: "LOW", explanation: "No data" },
    findings = [],
    web_scan,
    open_ports = [],
    services = [],
    os_info = {},
  } = useMemo(() => scanDetails || {}, [scanDetails]);

  if (!scanDetails) return <p>No scan selected</p>;

  // Group findings by severity
  const groupedFindings = findings.reduce((acc, f) => {
    const sev = f.severity || "LOW";
    if (!acc[sev]) acc[sev] = [];
    acc[sev].push(f);
    return acc;
  }, {});

  return (
    <div style={{ padding: "20px", color: "#fff" }}>
      <h2>🔍 Scan Result</h2>
      <p>
        <b>Target:</b> {target}
      </p>
      <p>
        <b>Scan Type:</b> {scan_type}
      </p>

      {/* Risk Summary */}
      <div
        style={{
          border: `2px solid ${severityColors[risk.level] || "#fff"}`,
          padding: "10px",
          borderRadius: "8px",
          marginBottom: "20px",
          maxWidth: "400px",
        }}
      >
        <h3>⚠️ Risk Summary</h3>
        <p>
          <b>Score:</b> {risk.score}
        </p>
        <p>
          <b>Level:</b>{" "}
          <span
            style={{
              color: severityColors[risk.level] || "#fff",
              fontWeight: "bold",
            }}
          >
            {risk.level}
          </span>
        </p>
        <p>
          <b>Explanation:</b> {risk.explanation}
        </p>
      </div>

      {/* Web Scan Info */}
      {web_scan && (
        <div style={{ marginBottom: "20px" }}>
          <h3>🌐 Web Info</h3>
          <p>
            <b>Title:</b> {web_scan.title || "N/A"}
          </p>
          <p>
            <b>Status Code:</b> {web_scan.status_code || "N/A"}
          </p>
          <p>
            <b>Technologies:</b>{" "}
            {web_scan.technologies?.length > 0
              ? web_scan.technologies.join(", ")
              : "N/A"}
          </p>
        </div>
      )}

      {/* System/Network Info */}
      {(open_ports.length > 0 ||
        services.length > 0 ||
        Object.keys(os_info).length > 0) && (
        <div style={{ marginBottom: "20px" }}>
          <h3>🖥 System / Network Info</h3>
          {open_ports.length > 0 && (
            <p>
              <b>Open Ports:</b> {open_ports.join(", ")}
            </p>
          )}
          {services.length > 0 && (
            <p>
              <b>Services:</b> {services.join(", ")}
            </p>
          )}
          {Object.keys(os_info).length > 0 && (
            <p>
              <b>OS Info:</b> {os_info.name || ""} {os_info.version || ""}
            </p>
          )}
        </div>
      )}

      {/* Vulnerabilities */}
      <div>
        <h3>🚨 Vulnerabilities / Findings</h3>
        {Object.keys(groupedFindings).length === 0 ? (
          <p>No vulnerabilities found</p>
        ) : (
          Object.keys(severityColors).map((level) => {
            const items = groupedFindings[level];
            if (!items || items.length === 0) return null;

            return (
              <div key={level} style={{ marginBottom: "15px" }}>
                <h4 style={{ color: severityColors[level] }}>
                  {level} ({items.length})
                </h4>
                {items.map((v, i) => (
                  <div
                    key={i}
                    style={{
                      border: `1px solid ${severityColors[level]}`,
                      padding: "10px",
                      borderRadius: "8px",
                      marginBottom: "8px",
                      backgroundColor: "#111827",
                    }}
                  >
                    <p>
                      <b>{v.cve || v.cve_id || "N/A"}</b>
                    </p>
                    <p>{v.description || v.evidence || ""}</p>
                    <p>
                      <b>Exploit Available:</b>{" "}
                      {v.exploits_available?.length > 0 ? "⚠️ Yes" : "No"}
                    </p>
                    <p>
                      <b>Fix:</b> {v.remediation || "N/A"}
                    </p>
                  </div>
                ))}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ScanResult;
