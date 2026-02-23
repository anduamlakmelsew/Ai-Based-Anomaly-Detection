import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function TrafficGraph() {
  const data = [
    { date: "2026-02-15", anomalies: 5 },
    { date: "2026-02-16", anomalies: 8 },
    { date: "2026-02-17", anomalies: 3 },
    { date: "2026-02-18", anomalies: 10 },
    { date: "2026-02-19", anomalies: 6 },
    { date: "2026-02-20", anomalies: 12 },
  ];

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Anomaly Trend Graph</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
        >
          <CartesianGrid stroke="#f5f5f5" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="anomalies"
            stroke="#dc2626"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TrafficGraph;
