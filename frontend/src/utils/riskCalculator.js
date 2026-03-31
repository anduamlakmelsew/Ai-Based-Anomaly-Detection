export const getSeverity = (score) => {
  if (score < 20) return "Low";
  if (score < 50) return "Medium";
  return "High";
};
