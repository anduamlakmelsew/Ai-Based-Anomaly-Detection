import { useEffect, useState } from "react";
import { getScanHistory } from "../../services/scanService";

const ScanHistory = ({ onSelectScan }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchHistory = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await getScanHistory();

        // Normalize response: handle { success: true, data: [...] } or array
        const scans = Array.isArray(response) ? response : response?.data || [];

        // Remove duplicates by ID
        const uniqueScans = Array.from(
          new Map(scans.map((s) => [s.id, s])).values(),
        );

        if (isMounted) setHistory(uniqueScans);
      } catch (err) {
        console.error("Error fetching history:", err);
        if (isMounted) setError("Failed to fetch scan history.");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchHistory();

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) return <p>Loading scan history...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Scan History</h2>

      {history.length === 0 ? (
        <p>No scans found.</p>
      ) : (
        <table
          border="1"
          cellPadding="10"
          style={{ width: "100%", borderCollapse: "collapse" }}
        >
          <thead>
            <tr>
              <th>ID</th>
              <th>Target</th>
              <th>Type</th>
              <th>Risk</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {history.map((scan) => (
              <tr
                key={scan.id}
                onClick={() => onSelectScan && onSelectScan(scan)}
                style={{ cursor: "pointer" }}
              >
                <td>{scan.id}</td>
                <td>{scan.target || "N/A"}</td>
                <td>{scan.scan_type || "N/A"}</td>
                <td>{scan.risk?.score ?? 0}</td>
                <td>{scan.status || "N/A"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ScanHistory;
