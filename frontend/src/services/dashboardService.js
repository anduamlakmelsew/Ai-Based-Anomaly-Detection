import API from "./api";

/**
 * Get comprehensive dashboard statistics with AI insights
 */
export const getDashboardStats = async () => {
  const res = await API.get("/dashboard/stats");
  return res.data;
};

/**
 * Get quick summary for dashboard header
 */
export const getDashboardSummary = async () => {
  const res = await API.get("/dashboard/summary");
  return res.data;
};

/**
 * Get activity feed for dashboard activity log
 */
export const getActivityFeed = async (limit = 20) => {
  const res = await API.get(`/dashboard/activity?limit=${limit}`);
  return res.data;
};

/**
 * Get AI-powered insights and recommendations
 */
export const getAIInsights = async () => {
  const res = await API.get("/dashboard/ai-insights");
  return res.data;
};

/**
 * Legacy function - kept for backwards compatibility
 * @deprecated Use getDashboardStats() instead
 */
export const getDashboardData = async () => {
  const res = await API.get("/scan/history");
  return res.data;
};
