import api from "./api";

export const getAnomalies = async () => {
  const response = await api.get("/anomalies");
  return response.data;
};

export const getModelPerformance = async () => {
  const response = await api.get("/anomalies/model-performance");
  return response.data;
};

export const getTrafficGraph = async () => {
  const response = await api.get("/anomalies/traffic");
  return response.data;
};
