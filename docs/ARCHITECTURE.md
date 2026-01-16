# Architecture

Detailed system architecture and component design of MyDB.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interfaces                      │
├──────────────┬──────────────────┬──────────────────────┤
│ REPL (CLI)   │  REST API        │  React Frontend      │
│ Terminal     │  FastAPI         │  Web Browser         │
└──────┬───────┴────────┬─────────┴──────────┬───────────┘
       │                │                    │
       └────────────────┼────────────────────┘
                        │
                        ↓
            ┌───────────────────────┐
            │   Query Executor       │
            │  (Orchestrator)        │
            └───────────┬───────────┘
                        │
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
    ┌─────────┐   ┌──────────┐   ┌─────────┐
    │ Parser  │   │  Schema  │   │ Indexer │
    └─────────┘   │  Manager │   └─────────┘
                  └──────────┘
                        │
                        ↓
                 ┌─────────────┐
                 │   Storage   │
                 │   Engine    │
                 └─────────────┘
                        │
                        ↓
                  [JSON File]
```

---

## Core Components

### 1. Storage Engine

**File:** `database/storage.py`

**Responsibility:** Physical data storage and retrieval

**Data Structure:**

```python
{
    'users': [
        {'id': 1, 'name': 'John', 'email': 'john@example.com'},
        {'id': 2, 'name': 'Jane', 'email': 'jane@example.com'}
    ],
    'posts': [
        {'id': 1, 'user_id': 1, 'title': 'Hello'},
        {'id': 2, 'user_id': 1, 'title': 'World'}
    ]
}
```

**Key Methods:**

- `create_table(name)` - Initialize empty table (empty list)
- `insert_row(table, row)` - Append row dict to table list
- `get_all_rows(table)` - Return copy of all rows
- `update_rows(table, rows)` - Replace entire table contents
- `drop_table(name)` - Remove table from storage
- `load_from_disk()` - Deserialize JSON file
- `_save_to_disk()` - Serialize to JSON file

**Design Rationale:**

**Why dictionaries?**

- Fast key-based access O(1)
- Natural JSON serialization
- Self-documenting (column names visible)

**Why lists of dicts?**

- Ordered (maintain insertion order)
- Easy iteration
- Column names in each row

**Why JSON persistence?**

- Human-readable
- Easy to debug
- Cross-platform
- Python native support

**Trade-offs:**
| Pros | Cons |
|------|------|
| Simple implementation | Limited to RAM size |
| Fast for small data | Slow JSON serialization |
| Easy debugging | No crash recovery |
| Portable format | Single-threaded only |

---

### 2. Schema Manager

**File:** `database/schema.py`

**Responsibility:** Table structure definitions and validation

**Key Classes:**

**Column:**

```python
@dataclass
class Column:
    name: str                      # Column name
    data_type: DataType            # INTEGER, VARCHAR, etc.
    max_length: Optional[int]      # For VARCHAR(n)
    nullable: bool                 # Can be NULL?
```

**TableSchema:**

```python
@dataclass
class TableSchema:
    name: str                      # Table name
    columns: List[Column]          # Column definitions
    primary_key: Optional[str]     # PK column name
    unique_constraints: Set[str]   # Unique column names
    indexes: Set[str]              # Indexed columns
```

**Key Methods:**

- `create_table_schema()` - Define new table structure
- `validate_row()` - Check row matches schema
- `get_column()` - Find column definition by name
- `get_column_names()` - List all column names

**Validation Process:**

```
1. Check all required columns present
2. Check no extra columns exist
3. Validate each value's data type
4. Check VARCHAR max length
5. Return validated row dict
```

**Design Rationale:**

**Why separate from storage?**

- Separation of concerns
- Reusable validation logic
- Matches real DB design (system catalogs)

**Why dataclasses?**

- Less boilerplate
- Automatic **init**, **repr**
- Type hints built-in

**Why validate early?**

- Fail fast
- Better error messages
- Data integrity

---

### 3. Index Manager

**File:** `database/indexer.py`

**Responsibility:** Fast data lookup via indexes

**Data Structure:**

```python
# Hash index
{
    1: [0],      # value 1 is at row index 0
    5: [1],      # value 5 is at row index 1
    3: [2],      # value 3 is at row index 2
    7: [3, 5]    # value 7 is at indices 3 and 5 (non-unique)
}
```

**Index Class:**

```python
class Index:
    table_name: str
    column_name: str
    unique: bool
    index_map: Dict[Any, List[int]]  # value -> row indices
```

**Key Methods:**

- `build(rows)` - Create index from scratch
- `add(value, row_idx)` - Add entry to index
- `remove(value, row_idx)` - Remove entry
- `lookup(value)` - Find row indices O(1)

**Index Types:**

- **Primary Key Index**: Unique, auto-created
- **Unique Constraint Index**: Unique, auto-created
- **Regular Index**: Future enhancement

**Performance:**

```python
# Without index (linear scan) - O(n)
for row in rows:
    if row['id'] == 5:
        return row

# With index (hash lookup) - O(1)
row_idx = index.lookup(5)[0]
return rows[row_idx]
```

**Design Rationale:**

**Why hash indexes?**

- O(1) average lookup
- Simple implementation
- Perfect for equality checks
- Low memory overhead

**Why store row indices?**

- Indirection layer
- Flexible (can rearrange rows)
- Small memory footprint

**Why rebuild on changes?**

- Simplest implementation
- Acceptable for small datasets
- Could optimize later

**Limitations:**

- Can't do range queries (WHERE age > 25)
- Hash collisions (rare with Python dict)
- Memory overhead

---

### 4. SQL Parser

**File:** `database/parser.py`

**Responsibility:** Convert SQL text to structured commands

**External Dependency:** `sqlparse` library

**Parser Flow:**

```
SQL Text
    ↓
[sqlparse tokenization]
    ↓
Token Tree
    ↓
[Extract relevant parts]
    ↓
Command Dict
```

**Example:**

```sql
SELECT name, email FROM users WHERE id = 1
```

**Becomes:**

```python
{
    'command': 'SELECT',
    'table': 'users',
    'columns': ['name', 'email'],
    'where': {
        'column': 'id',
        'operator': '=',
        'value': 1
    }
}
```

**Supported Commands:**

- CREATE TABLE
- DROP TABLE
- INSERT
- SELECT
- UPDATE
- DELETE

**Key Methods:**

- `parse(sql)` - Main entry point
- `_parse_create_table()` - Handle CREATE TABLE
- `_parse_select()` - Handle SELECT
- `_parse_where()` - Parse WHERE clauses
- `_parse_join()` - Parse JOIN clauses
- `_parse_value()` - Convert string to typed value

**Type Conversion:**

```python
'5'         → 5 (int)
'3.14'      → 3.14 (float)
"'hello'"   → 'hello' (str)
'TRUE'      → True (bool)
'NULL'      → None
```

**Design Rationale:**

**Why use sqlparse?**

- Full SQL parser would take weeks
- Handles edge cases (quotes, comments)
- Industry-standard tokenization

**Why not write own parser?**

- SQL grammar is huge (500+ pages)
- Many edge cases
- Not the focus of this project

**Trade-offs:**
| Approach | Pros | Cons |
|----------|------|------|
| sqlparse | Fast to implement, robust | Limited control |
| Custom parser | Full control | Weeks of work |
| Regex | Very simple | Fragile, unmaintainable |

---

### 5. Query Executor

**File:** `database/executor.py`

**Responsibility:** Execute parsed commands

**Architecture:**

```python
class QueryExecutor:
    storage: StorageEngine
    schema_mgr: SchemaManager
    index_mgr: IndexManager
```

**Execution Flow:**

**CREATE TABLE:**

```
1. Parse column definitions
2. Create schema
3. Create storage table
4. Create indexes (PK, UNIQUE)
5. Return success
```

**INSERT:**

```
1. Get table schema
2. Build row dict from values
3. Validate against schema
4. Check unique constraints via indexes
5. Insert into storage
6. Update all indexes
7. Return success
```

**SELECT:**

```
1. Get all rows from storage
2. Apply WHERE filter
3. Apply JOIN if present
4. Select requested columns
5. Return rows
```

**UPDATE:**

```
1. Get all rows
2. Filter by WHERE
3. Apply updates to matching rows
4. Validate updated rows
5. Save to storage
6. Rebuild indexes
7. Return count
```

**DELETE:**

```
1. Get all rows
2. Filter out rows matching WHERE
3. Save remaining rows
4. Rebuild indexes
5. Return count
```

**JOIN Implementation (Nested Loop):**

```python
result = []
for left_row in left_table:
    for right_row in right_table:
        if left_row[left_col] == right_row[right_col]:
            combined = {**left_row, **right_row}
            result.append(combined)
return result
```

**Design Rationale:**

**Why coordinate three components?**

- Single source of truth
- Maintains consistency
- Enforces constraints

**Why validate before storing?**

- Fail fast
- Better error messages
- Prevents invalid data

**Why rebuild indexes on changes?**

- Simplest implementation
- Guarantees consistency
- Acceptable for small data

**Error Handling:**

```python
try:
    # Execute operation
    result = self._execute_insert(...)
    return {'success': True, 'message': '...'}
except Exception as e:
    return {'success': False, 'message': str(e)}
```

---

## User Interfaces

### REPL (Read-Eval-Print Loop)

**File:** `database/repl.py`

**Components:**

- Input reader (multi-line support)
- Command router (SQL vs special commands)
- Result formatter (ASCII tables)
- Help system

**Flow:**

```
Read Command
    ↓
[Is it special command?]
    Yes → Execute directly
    No  → Parse SQL
    ↓
Execute
    ↓
Format Results
    ↓
Print
    ↓
Loop
```

**Special Features:**

- Multi-line input (until `;`)
- Pretty-printed tables
- Special commands (`\tables`, `\describe`)
- Keyboard shortcuts (Ctrl+C, Ctrl+D)

---

### REST API

**File:** `api/main.py`

**Framework:** FastAPI

**Endpoints:**

```
GET  /                    Health check
POST /query               Execute SQL
GET  /tables              List all tables
GET  /tables/{name}       Get table details
DELETE /tables/{name}     Drop table
```

**Request/Response:**

```python
# Request
{
    "sql": "SELECT * FROM users"
}

# Response
{
    "success": true,
    "message": "Found 2 row(s)",
    "data": [...],
    "columns": [...]
}
```

**Features:**

- Automatic validation (Pydantic)
- CORS support for frontend
- Auto-generated docs (Swagger)
- JSON serialization

---

### React Frontend

**Directory:** `frontend/src`

**Component Tree:**

```
App
├── TableList (sidebar)
├── QueryPanel (top)
└── ResultsPanel (bottom)
```

**State Management:**

```javascript
// Lift state to App
const [tables, setTables] = useState([])
const [result, setResult] = useState(null)

// Pass down as props
<TableList tables={tables} />
<ResultsPanel result={result} />
```

**Data Flow:**

```
User Action (click)
    ↓
Event Handler
    ↓
API Call (fetch)
    ↓
Update State
    ↓
Re-render Components
```

---

## Data Flow Example

**Complete flow for:** `INSERT INTO users VALUES (1, 'John', 'john@example.com')`

```
1. User types in REPL/Web/API
    ↓
2. Parser.parse(sql)
    → {'command': 'INSERT', 'table': 'users', ...}
    ↓
3. Executor.execute(parsed)
    ↓
4. Schema.validate_row(row)
    → {'id': 1, 'name': 'John', 'email': 'john@example.com'}
    ↓
5. Index.lookup('john@example.com')  # Check unique
    → [] (not found, OK to insert)
    ↓
6. Storage.insert_row('users', row)
    → Append to list
    ↓
7. Index.add('john@example.com', row_index)
    → Update index map
    ↓
8. Storage._save_to_disk()
    → Write JSON file
    ↓
9. Return {'success': True, 'message': 'Row inserted'}
```

---

## Design Patterns Used

### 1. Separation of Concerns

Each module has one responsibility:

- Storage → Physical data
- Schema → Structure
- Index → Fast lookup
- Parser → SQL conversion
- Executor → Coordination

### 2. Dependency Injection

```python
# Executor receives dependencies
def __init__(self, storage, schema_mgr, index_mgr):
    self.storage = storage
    self.schema_mgr = schema_mgr
    self.index_mgr = index_mgr
```

**Benefits:**

- Testable (can mock dependencies)
- Flexible (can swap implementations)
- Clear dependencies

### 3. Command Pattern

```python
# Parse SQL into command object
command = parser.parse(sql)

# Execute command
result = executor.execute(command)
```

### 4. Strategy Pattern

```python
# Different execution strategies
if command == 'SELECT':
    return self._execute_select(parsed)
elif command == 'INSERT':
    return self._execute_insert(parsed)
```

---

## Performance Characteristics

### Time Complexity

| Operation           | Without Index  | With Index     |
| ------------------- | -------------- | -------------- |
| INSERT              | O(1)           | O(1)           |
| SELECT (no WHERE)   | O(n)           | O(n)           |
| SELECT (WHERE id =) | O(n)           | O(1)           |
| UPDATE              | O(n) + rebuild | O(n) + rebuild |
| DELETE              | O(n) + rebuild | O(n) + rebuild |
| JOIN                | O(n × m)       | O(n × m)       |

**n** = number of rows in table  
**m** = number of rows in joined table

### Space Complexity

**Storage:** O(n) where n = total rows across all tables

**Indexes:** O(i × r) where:

- i = number of indexed columns
- r = number of rows

**Example:**

```
1000 rows with 3 indexed columns
= 3 × 1000 = 3000 index entries
≈ 24KB (assuming 8 bytes per entry)
```

---

## Scaling Limits

**Current System:**

- **Max rows**: ~100,000 (limited by RAM and JSON serialization)
- **Max tables**: ~100 (performance degrades)
- **Max indexes**: No hard limit
- **Concurrent users**: 1 (single-threaded)

**Why these limits?**

- In-memory storage
- JSON serialization overhead
- No query optimization
- Nested loop joins

**Production DBs handle:**

- Billions of rows
- Thousands of tables
- Millions of concurrent connections
- Petabytes of data

---

## Thread Safety

**Current:** Not thread-safe

**Issues:**

- Shared mutable state
- No locking
- Race conditions possible

**Example race condition:**

```python
# Thread 1
rows = storage.get_all_rows('users')
rows.append(new_row)  # ← Race!
storage.update_rows('users', rows)

# Thread 2
rows = storage.get_all_rows('users')
rows.append(another_row)  # ← Race!
storage.update_rows('users', rows)

# Result: One insert lost!
```

**Solution (future):**

- Add locking (threading.Lock)
- Or use MVCC (Multi-Version Concurrency Control)
- Or process-based isolation

---

## Extension Points

### Adding New Data Types

1. Add to `DataType` enum
2. Add validation in `Column.validate_value()`
3. Add parsing in `SQLParser._parse_value()`

### Adding New SQL Commands

1. Add parsing in `SQLParser`
2. Add execution in `QueryExecutor`
3. Add tests

### Adding New Index Types

1. Create new `Index` subclass
2. Implement `build()`, `add()`, `lookup()`
3. Update `IndexManager`
