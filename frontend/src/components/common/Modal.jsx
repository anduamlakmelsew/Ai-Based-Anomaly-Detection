import React from "react";

function Modal({ isOpen, title, children, onClose }) {
  if (!isOpen) return null;

  return (
    <div style={modalOverlayStyle}>
      <div style={modalContentStyle}>
        <div style={modalHeaderStyle}>
          <h3>{title}</h3>
          <button onClick={onClose} style={closeButtonStyle}>
            &times;
          </button>
        </div>
        <div style={modalBodyStyle}>{children}</div>
      </div>
    </div>
  );
}

const modalOverlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  background: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
};

const modalContentStyle = {
  background: "#fff",
  padding: "20px",
  borderRadius: "8px",
  width: "500px",
  maxWidth: "90%",
};

const modalHeaderStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "10px",
};

const modalBodyStyle = {
  maxHeight: "400px",
  overflowY: "auto",
};

const closeButtonStyle = {
  border: "none",
  background: "transparent",
  fontSize: "20px",
  cursor: "pointer",
};

export default Modal;
