import './ResultsPanel.css';

/**
 * Query Results Display
 * =====================
 *
 * Shows the results of SQL queries.
 *
 * Displays:
 * - Success/error messages
 * - Data table (for SELECT queries)
 * - Row counts
 *
 * Why separate component? Keeps result rendering logic isolated.
 */
function ResultsPanel({ result }) {
  // No result yet - show empty state
  if (!result) {
    return (
      <div className="results-panel">
        <div className="results-empty">
          <p>💡 Execute a query to see results</p>
        </div>
      </div>
    );
  }

  // Query failed - show error
  if (!result.success) {
    return (
      <div className="results-panel">
        <div className="results-header error">
          <span className="status-icon">❌</span>
          <span className="status-text">Error</span>
        </div>
        <div className="results-message error-message">{result.message}</div>
      </div>
    );
  }

  // Query succeeded - show success message and data
  return (
    <div className="results-panel">
      {/* Success header */}
      <div className="results-header success">
        <span className="status-icon">✅</span>
        <span className="status-text">Success</span>
      </div>

      {/* Message (e.g., "1 row inserted") */}
      <div className="results-message success-message">{result.message}</div>

      {/* Data table (only for SELECT queries) */}
      {result.data && result.data.length > 0 && (
        <div className="results-table-container">
          <DataTable data={result.data} columns={result.columns} />
        </div>
      )}

      {/* No data message for successful non-SELECT queries */}
      {result.data && result.data.length === 0 && (
        <div className="results-no-data">No rows returned</div>
      )}
    </div>
  );
}

/**
 * Data Table Component
 * ====================
 *
 * Renders query results in a table format.
 *
 * Why separate component? Makes ResultsPanel cleaner.
 */
function DataTable({ data, columns }) {
  // Use columns from result, or infer from first row
  const tableColumns = columns || Object.keys(data[0] || {});

  return (
    <table className="data-table">
      <thead>
        <tr>
          {tableColumns.map((col) => (
            <th key={col}>{col}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {tableColumns.map((col) => (
              <td key={col}>
                {/* Format values nicely */}
                {formatValue(row[col])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/**
 * Format a value for display
 *
 * Handles:
 * - null values (show as "NULL")
 * - booleans (show as "true"/"false")
 * - long strings (could truncate if needed)
 */
function formatValue(value) {
  if (value === null || value === undefined) {
    return <span className="null-value">NULL</span>;
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  return String(value);
}

export default ResultsPanel;
