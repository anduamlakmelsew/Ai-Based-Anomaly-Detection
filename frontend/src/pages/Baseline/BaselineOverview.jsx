import RiskScoreCard from "../Dashboard/RiskScoreCard";
import Table from "../../components/common/Table";

function BaselineOverview() {
  // Sample data for table
  const columns = [
    "Configuration",
    "Expected Value",
    "Current Value",
    "Status",
  ];
  const data = [
    {
      Configuration: "Firewall Enabled",
      "Expected Value": "Yes",
      "Current Value": "Yes",
      Status: "Compliant",
    },
    {
      Configuration: "SSH Password Auth",
      "Expected Value": "Disabled",
      "Current Value": "Enabled",
      Status: "Non-Compliant",
    },
    {
      Configuration: "Antivirus Installed",
      "Expected Value": "Yes",
      "Current Value": "Yes",
      Status: "Compliant",
    },
  ];

  return (
    <div style={{ padding: "20px" }}>
      <h2>Baseline Compliance Overview</h2>

      {/* Compliance Cards */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "20px",
          flexWrap: "wrap",
        }}
      >
        <RiskScoreCard title="Total Configurations" value={3} color="#2563eb" />
        <RiskScoreCard title="Compliant" value={2} color="#16a34a" />
        <RiskScoreCard title="Non-Compliant" value={1} color="#dc2626" />
      </div>

      {/* Configuration Table */}
      <div style={{ marginTop: "40px" }}>
        <h3>Configuration Details</h3>
        <Table columns={columns} data={data} />
      </div>
    </div>
  );
}

export default BaselineOverview;
