import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { uploadAIModel, activateAIModel, reloadAIModel } from "../../services/aiModelService";
import "./ModelUpload.css";

const MODEL_TYPES = [
  { value: "network", label: "Network Scanner", color: "#3b82f6" },
  { value: "web", label: "Web Vulnerability", color: "#06b6d4" },
  { value: "system", label: "System Audit", color: "#8b5cf6" },
];

const ALLOWED_TYPES = [".pkl", ".joblib", ".h5", ".pt", ".pth"];

export default function ModelUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [modelType, setModelType] = useState("network");
  const [version, setVersion] = useState("");
  const [description, setDescription] = useState("");
  const [accuracy, setAccuracy] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success' | 'error' | null
  const [statusMessage, setStatusMessage] = useState("");
  const [uploadedModel, setUploadedModel] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
      if (!ALLOWED_TYPES.includes(ext)) {
        setUploadStatus("error");
        setStatusMessage(`Invalid file type. Allowed: ${ALLOWED_TYPES.join(", ")}`);
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setUploadStatus(null);
      setStatusMessage("");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
      if (!ALLOWED_TYPES.includes(ext)) {
        setUploadStatus("error");
        setStatusMessage(`Invalid file type. Allowed: ${ALLOWED_TYPES.join(", ")}`);
        return;
      }
      setSelectedFile(file);
      setUploadStatus(null);
      setStatusMessage("");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("error");
      setStatusMessage("Please select a model file");
      return;
    }

    if (!version) {
      setUploadStatus("error");
      setStatusMessage("Please enter a version (e.g., 2.0.0)");
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);
    setStatusMessage("Uploading model...");

    try {
      const metadata = {
        description: description || undefined,
        accuracy: accuracy ? parseFloat(accuracy) : undefined,
      };

      const response = await uploadAIModel(selectedFile, modelType, version, metadata);

      if (response.success) {
        setUploadStatus("success");
        setStatusMessage(response.message || "Model uploaded successfully!");
        setUploadedModel(response.data);

        // Optionally activate immediately
        if (response.data?.id) {
          try {
            await activateAIModel(response.data.id);
            await reloadAIModel(modelType);
            setStatusMessage("Model uploaded, activated, and ready to use!");
          } catch (activateErr) {
            console.warn("Model uploaded but activation failed:", activateErr);
            setStatusMessage("Model uploaded but activation failed. Activate manually.");
          }
        }

        // Reset form
        setSelectedFile(null);
        setVersion("");
        setDescription("");
        setAccuracy("");
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }

        if (onUploadSuccess) {
          onUploadSuccess(response.data);
        }
      } else {
        setUploadStatus("error");
        setStatusMessage(response.error || "Upload failed");
      }
    } catch (err) {
      console.error("Upload error:", err);
      setUploadStatus("error");
      setStatusMessage(err.response?.data?.error || err.message || "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="model-upload-container">
      <h2 className="model-upload-title">Upload AI Model</h2>
      <p className="model-upload-subtitle">
        Upload trained model files (.pkl, .joblib, .h5, .pt, .pth) for the AI pipeline
      </p>

      {/* Model Type Selection */}
      <div className="model-type-section">
        <label className="section-label">Model Type</label>
        <div className="model-type-buttons">
          {MODEL_TYPES.map((type) => (
            <button
              key={type.value}
              className={`model-type-btn ${modelType === type.value ? "active" : ""}`}
              style={{ 
                borderColor: type.color,
                backgroundColor: modelType === type.value ? type.color : "transparent"
              }}
              onClick={() => setModelType(type.value)}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* File Drop Zone */}
      <div
        className="file-drop-zone"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ALLOWED_TYPES.join(",")}
          onChange={handleFileSelect}
          style={{ display: "none" }}
        />
        <div className="drop-zone-content">
          {selectedFile ? (
            <div className="selected-file">
              <span className="file-icon">📦</span>
              <div className="file-info">
                <p className="file-name">{selectedFile.name}</p>
                <p className="file-size">{formatFileSize(selectedFile.size)}</p>
              </div>
              <button
                className="remove-file-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
              >
                ✕
              </button>
            </div>
          ) : (
            <>
              <span className="upload-icon">☁️</span>
              <p className="drop-text">Drop model file here or click to browse</p>
              <p className="file-types">Supported: {ALLOWED_TYPES.join(", ")}</p>
            </>
          )}
        </div>
      </div>

      {/* Form Fields */}
      <div className="form-fields">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="version">Version *</label>
            <input
              id="version"
              type="text"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              placeholder="e.g., 2.0.0"
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label htmlFor="accuracy">Accuracy (0-1)</label>
            <input
              id="accuracy"
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={accuracy}
              onChange={(e) => setAccuracy(e.target.value)}
              placeholder="e.g., 0.95"
              className="form-input"
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What's new in this version?"
            className="form-textarea"
            rows={3}
          />
        </div>
      </div>

      {/* Status Message */}
      <AnimatePresence>
        {uploadStatus && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`status-message ${uploadStatus}`}
          >
            {uploadStatus === "success" ? "✅" : "❌"} {statusMessage}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Button */}
      <button
        className="upload-btn"
        onClick={handleUpload}
        disabled={isUploading || !selectedFile || !version}
      >
        {isUploading ? (
          <>
            <span className="spinner"></span>
            Uploading...
          </>
        ) : (
          <>
            <span>📤</span>
            Upload Model
          </>
        )}
      </button>

      {/* Uploaded Model Info */}
      <AnimatePresence>
        {uploadedModel && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="uploaded-model-info"
          >
            <h4>📋 Uploaded Model Details</h4>
            <p><strong>Type:</strong> {uploadedModel.model_type}</p>
            <p><strong>Version:</strong> {uploadedModel.version}</p>
            <p><strong>File:</strong> {uploadedModel.filename}</p>
            <p><strong>Size:</strong> {formatFileSize(uploadedModel.file_size)}</p>
            <p><strong>Status:</strong> {uploadedModel.status}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
