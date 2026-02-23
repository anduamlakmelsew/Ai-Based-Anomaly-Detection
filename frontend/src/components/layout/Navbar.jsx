function Navbar() {
  return (
    <div
      style={{
        height: "60px",
        background: "#1f2937",
        color: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 20px",
        marginLeft: "220px",
      }}
    >
      <span>Our AI Based Security Tool</span>
      <span>Logged in User</span>
    </div>
  );
}

export default Navbar;
