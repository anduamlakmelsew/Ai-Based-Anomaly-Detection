import { useEffect, useState } from "react";
import { getAuditLogs } from "../../services/auditService";

export default function ActivityLog() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const fetchLogs = async () => {
      setLoading(true);
      setError("");

      try {
        const data = await getAuditLogs();
        if (isMounted) setLogs(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error("Failed to load audit logs:", e);
        if (isMounted) setError("Failed to load activity log.");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchLogs();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="card">
      <h3>📜 Activity Log</h3>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && logs.length === 0 && <p>No activity yet.</p>}

      {!loading && !error && logs.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{new Date(log.created_at).toLocaleString()}</td>
                <td>{log.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
