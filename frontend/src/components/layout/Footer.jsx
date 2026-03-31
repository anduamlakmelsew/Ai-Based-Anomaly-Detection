import React from "react";

function Footer() {
  return (
    <footer style={footerStyle}>
      &copy; {new Date().getFullYear()} Scanner App. All rights reserved.
    </footer>
  );
}

const footerStyle = {
  textAlign: "center",
  padding: "10px 0",
  backgroundColor: "#1E1E2F",
  color: "#fff",
  position: "fixed",
  bottom: 0,
  width: "100%",
};

export default Footer;
