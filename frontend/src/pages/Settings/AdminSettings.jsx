function AdminSettings() {
  return (
    <div>
      <h3>Admin Settings</h3>

      <label>Default Scan Interval (minutes):</label>
      <input type="number" />

      <br />
      <br />

      <label>Baseline Threshold (%):</label>
      <input type="number" />

      <br />
      <br />

      <button>Save System Settings</button>
    </div>
  );
}

export default AdminSettings;
