import './TableList.css';

/**
 * Table List Sidebar
 * ==================
 *
 * Displays all tables in the database.
 *
 * For each table, shows:
 * - Table name
 * - Row count
 * - Column names (with primary key indicator)
 *
 * Clicking a table loads its data.
 */
function TableList({ tables, onRefresh, onTableClick }) {
  return (
    <div className="table-list">
      {/* Header with refresh button */}
      <div className="table-list-header">
        <h2>📊 Tables</h2>
        <button
          className="btn-icon"
          onClick={onRefresh}
          title="Refresh table list"
        >
          🔄
        </button>
      </div>

      {/* Empty state when no tables exist */}
      {tables.length === 0 ? (
        <div className="empty-state">
          <p>No tables yet</p>
          <p className="hint">Create a table using CREATE TABLE</p>
        </div>
      ) : (
        // List of tables
        <div className="table-items">
          {tables.map((table) => (
            <div
              key={table.name}
              className="table-item"
              onClick={() => onTableClick(table.name)}
              role="button"
              tabIndex={0}
            >
              {/* Table name and row count */}
              <div className="table-header">
                <div className="table-name">{table.name}</div>
                <div className="table-info">
                  {table.row_count} row{table.row_count !== 1 ? 's' : ''}
                </div>
              </div>

              {/* Column badges */}
              <div className="table-columns">
                {table.columns.map((col) => (
                  <div key={col.name} className="column-badge">
                    <span className="column-name">{col.name}</span>
                    <span className="column-type">{col.type}</span>
                    {/* Show key icon for primary key */}
                    {col.name === table.primary_key && (
                      <span className="column-key" title="Primary Key">
                        🔑
                      </span>
                    )}
                    {/* Show unique icon for unique constraints */}
                    {table.unique_constraints?.includes(col.name) &&
                      col.name !== table.primary_key && (
                        <span className="column-unique" title="Unique">
                          ⭐
                        </span>
                      )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TableList;
