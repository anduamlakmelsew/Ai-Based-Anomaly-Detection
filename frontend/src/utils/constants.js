export const ROLES = {
  ADMIN: "admin",
  ANALYST: "analyst",
};

export const SEVERITY_LEVELS = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
};

export const SCAN_TYPES = {
  QUICK: "quick",
  FULL: "full",
};

export const ALERT_STATUS = {
  OPEN: "open",
  RESOLVED: "resolved",
  INVESTIGATING: "investigating",
};

export const API_ENDPOINTS = {
  AUTH_LOGIN: "/auth/login",
  AUTH_ME: "/auth/me",
  SCAN_START: "/scanner/start",
  SCAN_HISTORY: "/scanner/history",
  BASELINE_OVERVIEW: "/baseline/overview",
  ANOMALIES: "/anomalies",
  ALERTS: "/alerts",
};
