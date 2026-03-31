export const getRiskColor = (score) => {
  if (score < 3) return "#22c55e"; // green
  if (score < 7) return "#f59e0b"; // yellow
  return "#ef4444"; // red
};
