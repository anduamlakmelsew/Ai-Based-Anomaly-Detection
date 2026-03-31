import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function MainLayout({ children }) {
  return (
    <div style={styles.container}>
      <Sidebar />

      <div style={styles.main}>
        <Navbar />

        <div style={styles.content}>{children}</div>
      </div>
    </div>
  );
}

export default MainLayout;

const styles = {
  container: {
    display: "flex",
    height: "100vh",
  },
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },
  content: {
    padding: "20px",
    overflowY: "auto",
  },
};
