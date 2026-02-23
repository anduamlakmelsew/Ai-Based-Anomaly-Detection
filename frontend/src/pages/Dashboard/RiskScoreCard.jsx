function RiskScoreCard({ title, value, color }) {
  return (
    <div
      style={{
        backgroundColor: color || "#1f2937",
        color: "white",
        padding: "20px",
        borderRadius: "10px",
        flex: 1,
        textAlign: "center",
        minWidth: "150px",
      }}
    >
      <h3>{title}</h3>
      <p style={{ fontSize: "24px", fontWeight: "bold" }}>{value}</p>
    </div>
  );
}

export default RiskScoreCard;
