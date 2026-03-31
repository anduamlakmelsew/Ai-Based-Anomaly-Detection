import api from "./api";

export const getBaselineOverview = async () => {
  const response = await api.get("/baseline/overview");
  return response.data;
};

export const getBaselineVersions = async () => {
  const response = await api.get("/baseline/versions");
  return response.data;
};

export const getComplianceStandards = async () => {
  const response = await api.get("/baseline/compliance");
  return response.data;
};
