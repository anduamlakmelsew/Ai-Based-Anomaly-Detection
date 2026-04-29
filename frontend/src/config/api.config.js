/**
 * API Configuration
 * Centralized configuration for API and WebSocket connections
 */

// Backend API base URL
export const API_BASE_URL = "http://127.0.0.1:5003/api";

// Backend WebSocket URL
export const WEBSOCKET_URL = "http://127.0.0.1:5003";

// WebSocket configuration
export const WEBSOCKET_CONFIG = {
  transports: ["websocket", "polling"],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 3,
  timeout: 10000
};

// HTTP Polling configuration (fallback when WebSocket fails)
export const POLLING_CONFIG = {
  enabled: true,
  interval: 5000, // Poll every 5 seconds
  maxRetries: 3
};

// Feature flags
export const FEATURES = {
  websocketEnabled: true,
  httpPollingFallback: true,
  autoReconnect: true
};

export default {
  API_BASE_URL,
  WEBSOCKET_URL,
  WEBSOCKET_CONFIG,
  POLLING_CONFIG,
  FEATURES
};
