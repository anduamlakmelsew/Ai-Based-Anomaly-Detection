import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

export default function TrafficChart({ scans }) {
  if (!scans || scans.length === 0) {
    return <p style={{ color: "#fff" }}>No data for charts</p>;
  }

  // =========================
  // 📈 RISK TREND DATA
  // =========================
  const trendData = scans
    .slice(0, 10) // last 10 scans
    .reverse()
    .map((scan) => ({
      time: new Date(scan.timestamp).toLocaleTimeString(),
      risk: scan.risk?.score || 0,
    }));

  // =========================
  // 📊 SEVERITY DISTRIBUTION
  // =========================
  const severityMap = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
    INFO: 0,
  };

  scans.forEach((scan) => {
    (scan.findings || []).forEach((f) => {
      const sev = f.severity || "LOW";
      severityMap[sev]++;
    });
  });

  const severityData = Object.keys(severityMap).map((key) => ({
    name: key,
    value: severityMap[key],
  }));

  return (
    <div style={{ display: "grid", gap: "20px" }}>
      {/* ========================= */}
      {/* 📈 RISK TREND */}
      {/* ========================= */}
      <div className="card">
        <h4>📈 Risk Trend</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="risk" stroke="#22c55e" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ========================= */}
      {/* 📊 SEVERITY DISTRIBUTION */}
      {/* ========================= */}
      <div className="card">
        <h4>📊 Severity Distribution</h4>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={severityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
