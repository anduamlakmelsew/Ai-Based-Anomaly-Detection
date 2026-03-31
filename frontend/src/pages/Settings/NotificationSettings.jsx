function NotificationSettings() {
  return (
    <div>
      <h3>Notification Settings</h3>

      <label>
        <input type="checkbox" /> Email Alerts
      </label>

      <br />

      <label>
        <input type="checkbox" /> Report Notifications
      </label>

      <br />
      <br />

      <button>Save Preferences</button>
    </div>
  );
}

export default NotificationSettings;
