function UserSettings() {
  return (
    <div>
      <h3>User Settings</h3>
      <label>Username:</label>
      <input type="text" placeholder="Enter username" />

      <br />
      <br />

      <label>Email:</label>
      <input type="email" placeholder="Enter email" />

      <br />
      <br />

      <button>Save Changes</button>
    </div>
  );
}

export default UserSettings;
