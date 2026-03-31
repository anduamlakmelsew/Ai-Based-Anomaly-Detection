import React from "react";

function BaselineVersioning() {
  const versions = [
    { version: "1.0", date: "2026-01-15" },
    { version: "1.1", date: "2026-02-10" },
    { version: "2.0", date: "2026-03-05" },
  ];

  return (
    <div>
      <h2>Baseline Versioning</h2>
      <ul>
        {versions.map((v) => (
          <li key={v.version}>
            Version {v.version} - Released on {v.date}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BaselineVersioning;
