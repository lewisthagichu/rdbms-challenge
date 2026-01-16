import { useState } from 'react';
import './QueryPanel.css';

function QueryPanel({ onExecute, loading }) {
  const [sql, setSql] = useState('');

  const handleExecute = () => {
    if (sql.trim()) {
      onExecute(sql);
    }
  };

  const handleKeyPress = (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      handleExecute();
    }
  };

  const sampleQueries = [
    {
      name: 'Create Users Table',
      sql: `CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE
)`,
    },
    {
      name: 'Insert User',
      sql: "INSERT INTO users VALUES (1, 'John Doe', 'john@example.com')",
    },
    {
      name: 'Select All Users',
      sql: 'SELECT * FROM users',
    },
    {
      name: 'Create Posts Table',
      sql: `CREATE TABLE posts (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  title VARCHAR(200),
  content VARCHAR(1000)
)`,
    },
    {
      name: 'Join Users and Posts',
      sql: 'SELECT users.name, posts.title FROM users JOIN posts ON users.id = posts.user_id',
    },
  ];

  return (
    <div className="query-panel">
      <div className="query-header">
        <h2>SQL Query</h2>
        <span className="keyboard-hint">Ctrl+Enter to execute</span>
      </div>

      <textarea
        className="query-input"
        value={sql}
        onChange={(e) => setSql(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder="Enter SQL query here...
Example: SELECT * FROM users"
        rows={8}
      />

      <div className="query-actions">
        <button
          className="btn btn-primary"
          onClick={handleExecute}
          disabled={loading || !sql.trim()}
        >
          {loading ? 'Executing...' : 'Execute Query'}
        </button>

        <button
          className="btn btn-secondary"
          onClick={() => setSql('')}
          disabled={!sql.trim()}
        >
          Clear
        </button>
      </div>

      <div className="sample-queries">
        <h3>Sample Queries</h3>
        <div className="sample-query-list">
          {sampleQueries.map((query, index) => (
            <button
              key={index}
              className="sample-query-btn"
              onClick={() => setSql(query.sql)}
              title={query.sql}
            >
              {query.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default QueryPanel;
