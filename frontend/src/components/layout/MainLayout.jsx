import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

function MainLayout({ children }) {
  return (
    <>
      <Sidebar />
      <Navbar />
      <div style={{ marginLeft: "220px", padding: "20px", marginTop: "60px" }}>
        {children}
      </div>
    </>
  );
}

export default MainLayout;
