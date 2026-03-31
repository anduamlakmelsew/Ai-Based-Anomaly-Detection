import { getRiskColor } from "../../utils/riskColor";

export default function RiskScoreCard({ risk }) {
  const score = risk?.score || 0;
  const level = risk?.level || "LOW";
  const explanation = risk?.explanation || "";

  const color = getRiskColor(score);

  return (
    <div className="card">
      <h3>🔥 Risk Score</h3>

      <div style={{ fontSize: "40px", color, fontWeight: "bold" }}>{score}</div>

      <p style={{ color, fontWeight: "bold" }}>{level}</p>

      <p style={{ fontSize: "12px", opacity: 0.8 }}>{explanation}</p>

      <div
        style={{
          marginTop: "10px",
          height: "8px",
          background: "#334155",
          borderRadius: "5px",
        }}
      >
        <div
          style={{
            width: `${score}%`,
            height: "100%",
            background: color,
            borderRadius: "5px",
          }}
        />
      </div>
    </div>
  );
}
