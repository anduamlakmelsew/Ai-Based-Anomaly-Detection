export function formatDate(date) {
  if (!date) return "";

  const d = new Date(date);

  return d.toLocaleDateString() + " " + d.toLocaleTimeString();
}

export function formatPercentage(value) {
  if (value === null || value === undefined) return "0%";
  return `${value}%`;
}

export function formatRiskScore(score) {
  if (score >= 80) return "Critical";
  if (score >= 60) return "High";
  if (score >= 40) return "Medium";
  if (score >= 20) return "Low";
  return "Minimal";
}

export function capitalize(text) {
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}
