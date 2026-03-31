function SecuritySettings() {
  return (
    <div>
      <h3>Security Settings</h3>

      <label>Current Password:</label>
      <input type="password" />

      <br />
      <br />

      <label>New Password:</label>
      <input type="password" />

      <br />
      <br />

      <button>Update Password</button>
    </div>
  );
}

export default SecuritySettings;
