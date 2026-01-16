import { useState, useEffect } from 'react';
import './App.css';
import QueryPanel from './components/QueryPanel';
import TableList from './components/TableList';
import ResultsPanel from './components/ResultsPanel';

/**
 * Main App Component
 *
 * Structure:
 * - Left sidebar: List of tables
 * - Center: SQL query input
 * - Bottom: Query results
 */
function App() {
  const [tables, setTables] = useState([]);
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // API base URL
  const API_URL = 'http://localhost:8001';

  // Load tables on mount
  useEffect(() => {
    loadTables();
  }, []);

  /**
   * Fetch all tables from API
   */
  const loadTables = async () => {
    try {
      const response = await fetch(`${API_URL}/tables`);
      const data = await response.json();
      setTables(data.tables || []);
    } catch (error) {
      console.error('Error loading tables:', error);
    }
  };

  /**
   * Execute a SQL query
   */
  const executeQuery = async (sql) => {
    setLoading(true);
    setQueryResult(null);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sql }),
      });

      const result = await response.json();
      setQueryResult(result);

      // Reload tables if schema changed (CREATE/DROP)
      if (
        sql.trim().toUpperCase().startsWith('CREATE') ||
        sql.trim().toUpperCase().startsWith('DROP')
      ) {
        await loadTables();
      }
    } catch (error) {
      setQueryResult({
        success: false,
        message: `Error: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🗄️ MyDB - Simple Relational Database</h1>
        <p>A demonstration RDBMS with SQL support</p>
      </header>

      <div className="app-content">
        <aside className="sidebar">
          <TableList
            tables={tables}
            onRefresh={loadTables}
            onTableClick={(tableName) => {
              // Load table data when clicked
              executeQuery(`SELECT * FROM ${tableName}`);
            }}
          />
        </aside>

        <main className="main-content">
          <QueryPanel onExecute={executeQuery} loading={loading} />

          <ResultsPanel result={queryResult} />
        </main>
      </div>
    </div>
  );
}

export default App;
