import RiskScoreCard from "./RiskScoreCard";
import ActivityLog from "./ActivityLog";
import TrafficChart from "./TrafficChart";

function Dashboard() {
  return (
    <div style={{ padding: "20px" }}>
      <h2>Security Dashboard</h2>

      {/* Cards */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "20px",
          flexWrap: "wrap",
        }}
      >
        <RiskScoreCard title="Total Scans" value={128} color="#2563eb" />
        <RiskScoreCard title="Critical Alerts" value={5} color="#dc2626" />
        <RiskScoreCard
          title="System Safe Anomalies"
          value={12}
          color="#16a34a"
        />
      </div>

      {/* Recent Activity Table */}
      <ActivityLog />

      {/* Anomaly Detection Chart */}
      <TrafficChart />
    </div>
  );
}

export default Dashboard;
