import api from "./api";

/**
 * Upload a new AI model file
 * @param {File} file - The model file (.pkl, .joblib, .h5, .pt, .pth)
 * @param {string} modelType - 'network', 'web', or 'system'
 * @param {string} version - Model version (e.g., '2.0.0')
 * @param {object} metadata - Optional metadata { description, accuracy }
 */
export const uploadAIModel = async (file, modelType, version, metadata = {}) => {
  const formData = new FormData();
  formData.append("model", file);
  formData.append("model_type", modelType);
  formData.append("version", version);
  
  if (metadata.description) {
    formData.append("description", metadata.description);
  }
  if (metadata.accuracy) {
    formData.append("accuracy", metadata.accuracy);
  }

  const res = await api.post("/ai/upload-model", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;
};

/**
 * List all uploaded AI models
 * @param {string} type - Optional filter by model type
 */
export const listAIModels = async (type = null) => {
  const params = type ? { type } : {};
  const res = await api.get("/ai/models", { params });
  return res.data;
};

/**
 * Activate a specific model version
 * @param {number} modelId - The model ID to activate
 */
export const activateAIModel = async (modelId) => {
  const res = await api.post(`/ai/activate-model/${modelId}`);
  return res.data;
};

/**
 * Reload a model for immediate use
 * @param {string} modelType - 'network', 'web', or 'system'
 */
export const reloadAIModel = async (modelType) => {
  const res = await api.post(`/ai/reload-model/${modelType}`);
  return res.data;
};
