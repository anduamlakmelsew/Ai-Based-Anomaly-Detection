import api from "./api";

export const getAuditLogs = async () => {
  const res = await api.get("/audit/logs");
  return res.data;
};

