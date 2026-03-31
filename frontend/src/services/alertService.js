import api from "./api";

export const getAlerts = async () => {
  const response = await api.get("/alerts");
  return response.data;
};

export const getAlertDetails = async (alertId) => {
  const response = await api.get(`/alerts/${alertId}`);
  return response.data;
};

export const resolveAlert = async (alertId) => {
  const response = await api.put(`/alerts/${alertId}/resolve`);
  return response.data;
};
