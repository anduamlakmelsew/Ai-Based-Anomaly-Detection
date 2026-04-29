import api from "./api";

/**
 * Get all settings organized by category
 */
export const getAllSettings = async () => {
  const res = await api.get("/settings");
  return res.data;
};

/**
 * Get settings by category (scanner, ai, notification, security, system)
 */
export const getSettingsByCategory = async (category) => {
  const res = await api.get(`/settings/${category}`);
  return res.data;
};

/**
 * Update multiple settings at once
 */
export const updateSettings = async (settings) => {
  const res = await api.put("/settings", settings);
  return res.data;
};

/**
 * Update a single setting
 */
export const updateSetting = async (key, value) => {
  const res = await api.put(`/settings/${key}`, { value });
  return res.data;
};

/**
 * Get current user profile
 */
export const getProfile = async () => {
  const res = await api.get("/settings/profile");
  return res.data;
};

/**
 * Update user profile
 */
export const updateProfile = async (profileData) => {
  const res = await api.put("/settings/profile", profileData);
  return res.data;
};

/**
 * Change password
 */
export const changePassword = async (currentPassword, newPassword) => {
  const res = await api.post("/settings/change-password", {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return res.data;
};

/**
 * Get system status (admin only)
 */
export const getSystemStatus = async () => {
  const res = await api.get("/settings/system-status");
  return res.data;
};
