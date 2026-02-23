function Table({ columns, data }) {
  return (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        marginTop: "20px",
      }}
    >
      <thead style={{ backgroundColor: "#1f2937", color: "white" }}>
        <tr>
          {columns.map((col, idx) => (
            <th key={idx} style={{ padding: "10px", textAlign: "left" }}>
              {col}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx} style={{ borderBottom: "1px solid #e5e7eb" }}>
            {columns.map((col, cidx) => (
              <td key={cidx} style={{ padding: "10px" }}>
                {row[col]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default Table;
