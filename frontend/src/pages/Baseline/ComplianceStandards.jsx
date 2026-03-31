import React from "react";

function ComplianceStandards() {
  const standards = ["ISO 27001", "NIST 800-53", "CIS Benchmarks"];

  return (
    <div>
      <h2>Compliance Standards</h2>
      <ul>
        {standards.map((standard) => (
          <li key={standard}>{standard}</li>
        ))}
      </ul>
    </div>
  );
}

export default ComplianceStandards;
