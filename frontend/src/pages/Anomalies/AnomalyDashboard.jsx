import ModelPerformance from "./ModelPerformance";
import TrafficGraph from "./TrafficGraph";

function AnomalyDashboard() {
  return (
    <div style={{ padding: "20px" }}>
      <h2>Anomalies Module</h2>

      {/* Performance Cards */}
      <ModelPerformance />

      {/* Anomaly Graph */}
      <TrafficGraph />
    </div>
  );
}

export default AnomalyDashboard;
