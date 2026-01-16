# Usage Guide

Complete guide to using MyDB through all three interfaces: REPL, API, and Web Interface.

---

## Table of Contents

1. [REPL (Command Line)](#repl-command-line)
2. [REST API](#rest-api)
3. [Web Interface](#web-interface)
4. [Common Workflows](#common-workflows)

---

## REPL (Command Line)

The REPL (Read-Eval-Print Loop) provides an interactive command-line interface similar to `mysql` or `psql`.

### Starting the REPL

```bash
python3 -m database.repl
```

**Options:**

```bash
# In-memory only (no file persistence)
python3 -m database.repl --no-persist

# Custom database file
python3 -m database.repl --file mydata.json
```

### Basic Usage

**Multi-line SQL:**

```sql
mydb> CREATE TABLE users (
   ->   id INTEGER PRIMARY KEY,
   ->   name VARCHAR(100),
   ->   email VARCHAR(100) UNIQUE
   -> );
✓ Table 'users' created successfully
```

**Single-line SQL:**

```sql
mydb> INSERT INTO users VALUES (1, 'John Doe', 'john@example.com');
✓ Row inserted into 'users'
```

**Viewing results:**

```sql
mydb> SELECT * FROM users;
✓ Found 1 row(s)
id | name     | email
---------------------------------------
1  | John Doe | john@example.com

(1 row)
```

### Special Commands

**List tables:**

```sql
mydb> \tables;

Tables in database:

  📊 users (1 rows)
      Primary Key: id
      Columns: 3

  📊 posts (0 rows)
      Primary Key: id
      Columns: 3
```

**Describe table structure:**

```sql
mydb> \describe users;

Table: users
============================================================

Columns:
  • id: INTEGER [PRIMARY KEY]
  • name: VARCHAR(100)
  • email: VARCHAR(100) [UNIQUE]

Indexes:
  • id (UNIQUE)
  • email (UNIQUE)

Row count: 1
```

**Short form:**

```sql
mydb> \d users;
```

**Show help:**

```sql
mydb> \help;
```

**Exit:**

```sql
mydb> exit
# Or: quit, \q, or Ctrl+D
```

### Keyboard Shortcuts

- **Enter**: Submit single-line command (if it ends with `;`)
- **Enter** (multi-line): Continue to next line
- **Ctrl+C**: Cancel current command
- **Ctrl+D**: Exit REPL
- **Up/Down arrows**: Command history (if available)

### REPL Tips

1. **Use multi-line for readability:**

   ```sql
   CREATE TABLE products (
     id INTEGER PRIMARY KEY,
     name VARCHAR(200),
     price FLOAT,
     in_stock BOOLEAN
   );
   ```

2. **Test queries incrementally:**

   ```sql
   -- Start simple
   SELECT * FROM users;

   -- Add WHERE
   SELECT * FROM users WHERE id = 1;

   -- Add more columns
   SELECT name, email FROM users WHERE id = 1;
   ```

3. **Use \describe before querying:**
   ```sql
   \d users  -- See what columns exist
   SELECT name, email FROM users;  -- Use correct columns
   ```

---

## REST API

The FastAPI backend provides HTTP endpoints for programmatic access.

### Starting the API

```bash

# Method 1: With uvicorn (recommended for development)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
```

**The API will be available at:** `http://localhost:8001`

### API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Endpoints

#### 1. Health Check

**Request:**

```bash
GET http://localhost:8001/
```

**Response:**

```json
{
  "message": "MyDB API is running",
  "version": "1.0.0",
  "endpoints": ["/query", "/tables", "/tables/{name}"]
}
```

**cURL:**

```bash
curl http://localhost:8001/
```

#### 2. Execute SQL Query

**Request:**

```bash
POST http://localhost:8001/query
Content-Type: application/json

{
  "sql": "CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(100))"
}
```

**Response (Success):**

```json
{
  "success": true,
  "message": "Table 'users' created successfully"
}
```

**Response (Error):**

```json
{
  "success": false,
  "message": "Table 'users' already exists"
}
```

**Response (SELECT):**

```json
{
  "success": true,
  "message": "Found 2 row(s)",
  "data": [
    { "id": 1, "name": "John Doe" },
    { "id": 2, "name": "Jane Smith" }
  ],
  "columns": ["id", "name"]
}
```

**cURL Examples:**

```bash
# Create table
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(100))"}'

# Insert data
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "INSERT INTO users VALUES (1, '\''John Doe'\'')"}'

# Query data
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users"}'
```

#### 3. List All Tables

**Request:**

```bash
GET http://localhost:8001/tables
```

**Response:**

```json
{
  "tables": [
    {
      "name": "users",
      "row_count": 5,
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "nullable": true,
          "max_length": null
        },
        {
          "name": "name",
          "type": "VARCHAR",
          "nullable": true,
          "max_length": 100
        }
      ],
      "primary_key": "id",
      "unique_constraints": ["email"]
    }
  ]
}
```

**cURL:**

```bash
curl http://localhost:8001/tables
```

#### 4. Get Table Details

**Request:**

```bash
GET http://localhost:8001/tables/{table_name}
```

**Example:**

```bash
GET http://localhost:8001/tables/users
```

**Response:**

```json
{
  "name": "users",
  "columns": [...],
  "primary_key": "id",
  "unique_constraints": ["email"],
  "row_count": 5,
  "data": [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "Jane", "email": "jane@example.com"}
  ]
}
```

**cURL:**

```bash
curl http://localhost:8001/tables/users
```

#### 5. Drop Table

**Request:**

```bash
DELETE http://localhost:8001/tables/{table_name}
```

**Response:**

```json
{
  "message": "Table 'users' dropped successfully"
}
```

**cURL:**

```bash
curl -X DELETE http://localhost:8001/tables/users
```

### Using with JavaScript/Python

**JavaScript (fetch):**

```javascript
// Execute query
const response = await fetch('http://localhost:8001/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sql: 'SELECT * FROM users',
  }),
});

const result = await response.json();
console.log(result.data);
```

**Python (requests):**

```python
import requests

# Execute query
response = requests.post('http://localhost:8001/query', json={
    'sql': 'SELECT * FROM users'
})

result = response.json()
print(result['data'])
```

---

## Web Interface

The React frontend provides a visual interface for database operations.

### Starting the Web Interface

**Terminal 1 - Backend:**

```bash
python3 api/main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

**Open browser to:** `http://localhost:5173`

### Interface Overview

The web interface has three main areas:

```
┌─────────────────────────────────────────┐
│           Header / Title                │
├──────────┬──────────────────────────────┤
│          │                              │
│  Table   │      Query Panel             │
│  List    │                              │
│          ├──────────────────────────────┤
│          │                              │
│          │      Results Panel           │
│          │                              │
└──────────┴──────────────────────────────┘
```

### Features

#### 1. Table Browser (Left Sidebar)

- **View all tables** - See table names and row counts
- **Click to load** - Click any table to SELECT all rows
- **Column preview** - See column names and types
- **Primary key indicator** - 🔑 shows primary key columns
- **Refresh button** - 🔄 reload table list

#### 2. SQL Query Panel (Top Right)

- **Multi-line editor** - Write SQL queries
- **Execute button** - Run the query
- **Clear button** - Reset the editor
- **Sample queries** - One-click examples:
  - Create Users Table
  - Insert User
  - Select All Users
  - Update User
  - Create Posts Table
  - Insert Post
  - Join Users and Posts
  - Delete User

**Keyboard Shortcut:**

- **Ctrl+Enter** - Execute query

#### 3. Results Panel (Bottom Right)

- **Success/Error indication** - ✅ or ❌
- **Message display** - Operation result
- **Data table** - Pretty-printed results for SELECT
- **Row count** - Number of rows returned

### Typical Workflow

1. **Start with sample queries:**

   - Click "Create Users Table"
   - Click Execute (or Ctrl+Enter)
   - See success message

2. **Insert data:**

   - Click "Insert User" sample
   - Click Execute
   - See row inserted message

3. **View data:**

   - Click "Select All Users" sample
   - Click Execute
   - See data table with results

4. **Explore tables:**

   - Click "users" in left sidebar
   - Auto-executes SELECT \* FROM users
   - See all user data

5. **Modify and experiment:**
   - Edit sample queries
   - Try your own SQL
   - See results immediately

### Tips for Web Interface

1. **Use sample queries to learn:**

   - Each sample demonstrates a feature
   - Read the SQL to understand syntax

2. **Check table browser after schema changes:**

   - After CREATE TABLE, see it appear in sidebar
   - After DROP TABLE, see it disappear

3. **Read error messages:**

   - Errors show exactly what went wrong
   - Fix and try again

4. **Use Ctrl+Enter:**
   - Faster than clicking Execute

---

## Common Workflows

### Workflow 1: Create Database Schema

**Goal:** Set up tables for a blog application

**REPL:**

```sql
mydb> CREATE TABLE users (
   ->   id INTEGER PRIMARY KEY,
   ->   username VARCHAR(50) UNIQUE,
   ->   email VARCHAR(100) UNIQUE,
   ->   created_at VARCHAR(50)
   -> );
✓ Table 'users' created successfully

mydb> CREATE TABLE posts (
   ->   id INTEGER PRIMARY KEY,
   ->   user_id INTEGER,
   ->   title VARCHAR(200),
   ->   content VARCHAR(5000),
   ->   created_at VARCHAR(50)
   -> );
✓ Table 'posts' created successfully

mydb> \tables
Tables in database:

  📊 users (0 rows)
  📊 posts (0 rows)
```

**API:**

```bash
# Create users table
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(50) UNIQUE, email VARCHAR(100) UNIQUE)"}'

# Create posts table
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER, title VARCHAR(200))"}'

# Verify
curl http://localhost:8001/tables
```

### Workflow 2: Insert and Query Data

**Goal:** Add users and posts, then query them

**REPL:**

```sql
-- Insert users
mydb> INSERT INTO users VALUES (1, 'john_doe', 'john@example.com', '2024-01-01');
mydb> INSERT INTO users VALUES (2, 'jane_smith', 'jane@example.com', '2024-01-02');

-- Insert posts
mydb> INSERT INTO posts VALUES (1, 1, 'My First Post', 'Hello World!', '2024-01-03');
mydb> INSERT INTO posts VALUES (2, 1, 'Second Post', 'More content', '2024-01-04');
mydb> INSERT INTO posts VALUES (3, 2, 'Jane Post', 'Jane content', '2024-01-05');

-- Query specific user
mydb> SELECT * FROM users WHERE username = 'john_doe';

-- Query with JOIN
mydb> SELECT users.username, posts.title
   -> FROM users
   -> JOIN posts ON users.id = posts.user_id;
```

### Workflow 3: Update and Delete

**Goal:** Modify existing data

**REPL:**

```sql
-- Update user email
mydb> UPDATE users SET email = 'newemail@example.com' WHERE id = 1;

-- Verify update
mydb> SELECT * FROM users WHERE id = 1;

-- Delete a post
mydb> DELETE FROM posts WHERE id = 2;

-- Verify deletion
mydb> SELECT * FROM posts;
```

### Workflow 4: Test Constraints

**Goal:** Verify data integrity

**REPL:**

```sql
-- Try to insert duplicate primary key
mydb> INSERT INTO users VALUES (1, 'another_user', 'new@example.com', '2024-01-10');
✗ Duplicate primary key value: 1

-- Try to insert duplicate unique value
mydb> INSERT INTO users VALUES (3, 'third_user', 'john@example.com', '2024-01-10');
✗ Duplicate value 'john@example.com' for unique column 'email'

-- Success with unique values
mydb> INSERT INTO users VALUES (3, 'third_user', 'third@example.com', '2024-01-10');
✓ Row inserted into 'users'
```

### Workflow 5: Export/Backup Data

**Goal:** Save database to file

The REPL automatically saves to `database.json`.

**View the file:**

```bash
cat database.json
```

**Backup:**

```bash
cp database.json backup_$(date +%Y%m%d).json
```

**Restore:**

```bash
cp backup_20240101.json database.json
python3 -m database.repl
```

---

## Next Steps

- Learn SQL syntax: [SQL_REFERENCE.md](SQL_REFERENCE.md)
- Understand architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
