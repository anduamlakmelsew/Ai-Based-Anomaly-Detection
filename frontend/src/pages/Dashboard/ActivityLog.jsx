import Table from "../../components/common/Table";

function ActivityLog() {
  const columns = ["Time", "Target", "Scan Type", "Status"];
  const data = [
    {
      Time: "2026-02-20 10:00",
      Target: "192.168.1.10",
      "Scan Type": "System",
      Status: "Completed",
    },
    {
      Time: "2026-02-20 09:30",
      Target: "example.com",
      "Scan Type": "Web",
      Status: "Completed",
    },
    {
      Time: "2026-02-19 18:45",
      Target: "192.168.1.15",
      "Scan Type": "Network",
      Status: "Critical",
    },
  ];

  return (
    <div style={{ marginTop: "40px" }}>
      <h3>Recent Activity</h3>
      <Table columns={columns} data={data} />
    </div>
  );
}

export default ActivityLog;
