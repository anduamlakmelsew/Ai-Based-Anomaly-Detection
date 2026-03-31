import API from "./api";

export const getDashboardData = async () => {
  const res = await API.get("/scan/history");
  return res.data;
};
