import RiskScoreCard from "../Dashboard/RiskScoreCard";

function ModelPerformance() {
  return (
    <div
      style={{
        display: "flex",
        gap: "20px",
        flexWrap: "wrap",
        marginBottom: "20px",
      }}
    >
      <RiskScoreCard title="Model Accuracy" value="96%" color="#2563eb" />
      <RiskScoreCard title="Detected Anomalies" value={12} color="#dc2626" />
      <RiskScoreCard title="Detection Rate" value="92%" color="#16a34a" />
    </div>
  );
}

export default ModelPerformance;
