function Modal({ children, onClose }) {
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          background: "white",
          padding: "20px",
          borderRadius: "10px",
          width: "400px",
          maxWidth: "90%",
        }}
      >
        <button
          onClick={onClose}
          style={{
            float: "right",
            background: "transparent",
            border: "none",
            fontSize: "18px",
            cursor: "pointer",
          }}
        >
          ×
        </button>
        {children}
      </div>
    </div>
  );
}

export default Modal;
