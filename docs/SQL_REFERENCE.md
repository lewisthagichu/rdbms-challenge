# SQL Reference

Complete reference for all SQL commands supported by MyDB.

---

## Table of Contents

1. [Data Types](#data-types)
2. [CREATE TABLE](#create-table)
3. [DROP TABLE](#drop-table)
4. [INSERT](#insert)
5. [SELECT](#select)
6. [UPDATE](#update)
7. [DELETE](#delete)
8. [Constraints](#constraints)
9. [Operators](#operators)
10. [Examples](#examples)

---

## Data Types

MyDB supports four basic data types:

### INTEGER

**Description:** Whole numbers (positive or negative)

**Range:** -2,147,483,648 to 2,147,483,647 (32-bit signed integer)

**Examples:**

```sql
CREATE TABLE example (
    age INTEGER,
    count INTEGER,
    year INTEGER
);

INSERT INTO example VALUES (25, 100, 2024);
INSERT INTO example VALUES (-5, 0, 1999);
```

**Notes:**

- Stored as Python `int`
- Automatic type conversion from strings if possible

### VARCHAR(n)

**Description:** Variable-length character string

**Parameters:**

- `n` - Maximum length in characters

**Examples:**

```sql
CREATE TABLE example (
    name VARCHAR(100),
    email VARCHAR(255),
    code VARCHAR(10)
);

INSERT INTO example VALUES ('John Doe', 'john@example.com', 'ABC123');
```

**Notes:**

- Maximum length enforced during INSERT/UPDATE
- Empty strings allowed: `''`
- Quotes in strings: use `''` (two single quotes)

**String escaping:**

```sql
INSERT INTO users VALUES (1, 'O''Reilly', 'It''s great');
-- Stores: O'Reilly, It's great
```

### FLOAT

**Description:** Floating-point decimal numbers

**Examples:**

```sql
CREATE TABLE example (
    price FLOAT,
    temperature FLOAT,
    percentage FLOAT
);

INSERT INTO example VALUES (19.99, -5.5, 0.85);
INSERT INTO example VALUES (100.0, 37.5, 100.0);
```

**Notes:**

- Stored as Python `float`
- Standard floating-point precision issues apply
- Can also accept integers (will convert to float)

### BOOLEAN

**Description:** True or False values

**Accepted values:**

- `TRUE`, `true`, `1`, `'yes'` → True
- `FALSE`, `false`, `0`, `'no'` → False

**Examples:**

```sql
CREATE TABLE example (
    is_active BOOLEAN,
    is_admin BOOLEAN
);

INSERT INTO example VALUES (TRUE, FALSE);
INSERT INTO example VALUES (1, 0);
INSERT INTO example VALUES ('yes', 'no');
```

**Notes:**

- Stored as Python `bool`
- Case-insensitive

---

## CREATE TABLE

**Syntax:**

```sql
CREATE TABLE table_name (
    column1 datatype [constraint],
    column2 datatype [constraint],
    ...
);
```

### Basic Examples

**Simple table:**

```sql
CREATE TABLE users (
    id INTEGER,
    name VARCHAR(100)
);
```

**With primary key:**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);
```

**Multiple constraints:**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    age INTEGER,
    is_active BOOLEAN
);
```

### Notes

- Table names are case-sensitive
- Column names are case-sensitive
- PRIMARY KEY automatically creates an index
- UNIQUE constraints automatically create indexes
- Cannot create table that already exists

---

## DROP TABLE

**Syntax:**

```sql
DROP TABLE table_name;
```

### Examples

```sql
DROP TABLE users;
DROP TABLE posts;
```

### Notes

- **WARNING:** This deletes all data permanently
- Cannot be undone
- Removes schema, data, and indexes
- Error if table doesn't exist

---

## INSERT

**Syntax:**

```sql
-- All columns (in table order)
INSERT INTO table_name VALUES (value1, value2, ...);

-- Specific columns
INSERT INTO table_name (column1, column2) VALUES (value1, value2);
```

### Examples

**All columns:**

```sql
INSERT INTO users VALUES (1, 'John Doe', 'john@example.com');
```

**Specific columns:**

```sql
-- Other columns will be NULL
INSERT INTO users (id, name) VALUES (2, 'Jane Smith');
```

**Different data types:**

```sql
INSERT INTO products VALUES (1, 'Widget', 19.99, TRUE);
-- INTEGER, VARCHAR, FLOAT, BOOLEAN
```

**String with quotes:**

```sql
INSERT INTO posts VALUES (1, 'It''s a great day!', 'Content here');
```

### Validation

MyDB validates:

- **Data types:** VALUES must match column types
- **Primary key:** Must be unique
- **Unique constraints:** Must be unique
- **VARCHAR length:** Must not exceed max_length

**Error examples:**

```sql
-- Duplicate primary key
INSERT INTO users VALUES (1, 'Another', 'another@example.com');
✗ Duplicate primary key value: 1

-- Duplicate unique value
INSERT INTO users VALUES (2, 'User', 'john@example.com');
✗ Duplicate value 'john@example.com' for unique column 'email'

-- Wrong number of values
INSERT INTO users VALUES (3, 'Only Name');
✗ Expected 3 values, got 2

-- Type mismatch
INSERT INTO users VALUES ('not a number', 'Name', 'email@example.com');
✗ Cannot convert 'not a number' to INTEGER
```

---

## SELECT

**Syntax:**

```sql
SELECT column1, column2, ... FROM table_name [WHERE condition];
SELECT * FROM table_name [WHERE condition];
```

### Basic SELECT

**All columns:**

```sql
SELECT * FROM users;
```

**Specific columns:**

```sql
SELECT name, email FROM users;
```

**Single column:**

```sql
SELECT name FROM users;
```

### WHERE Clause

**Equality:**

```sql
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE name = 'John Doe';
SELECT * FROM users WHERE is_active = TRUE;
```

**Comparison operators:**

```sql
SELECT * FROM products WHERE price > 10.00;
SELECT * FROM products WHERE price < 100.00;
SELECT * FROM products WHERE price >= 50.00;
SELECT * FROM products WHERE price <= 75.00;
SELECT * FROM users WHERE id != 5;
```

**Multiple columns:**

```sql
SELECT name, email, age FROM users WHERE age > 18;
```

### JOIN

**Syntax:**

```sql
SELECT table1.column, table2.column
FROM table1
JOIN table2 ON table1.column = table2.column;
```

**Example:**

```sql
SELECT users.name, posts.title
FROM users
JOIN posts ON users.id = posts.user_id;
```

**With WHERE:**

```sql
SELECT users.name, posts.title
FROM users
JOIN posts ON users.id = posts.user_id
WHERE users.id = 1;
```

**Selecting multiple columns:**

```sql
SELECT users.name, users.email, posts.title, posts.content
FROM users
JOIN posts ON users.id = posts.user_id;
```

### Notes

- Column order in SELECT matches output order
- `*` returns all columns
- WHERE filters rows before returning
- JOIN creates a Cartesian product then filters by ON condition
- Only INNER JOIN is supported

---

## UPDATE

**Syntax:**

```sql
UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition;
```

### Examples

**Update single column:**

```sql
UPDATE users SET name = 'Jane Doe' WHERE id = 2;
```

**Update multiple columns:**

```sql
UPDATE products SET price = 24.99, in_stock = FALSE WHERE id = 1;
```

**Update all rows (dangerous!):**

```sql
UPDATE products SET in_stock = TRUE;
-- Updates EVERY row in the table
```

**Conditional update:**

```sql
UPDATE users SET is_active = FALSE WHERE age < 18;
```

### Notes

- WHERE clause is optional but recommended
- Without WHERE, updates ALL rows
- Values are validated against schema
- Returns count of updated rows
- Indexes are automatically updated

**Validation:**

```sql
-- Type mismatch
UPDATE users SET age = 'not a number' WHERE id = 1;
✗ Cannot convert 'not a number' to INTEGER

-- Unique constraint violation
UPDATE users SET email = 'existing@example.com' WHERE id = 2;
✗ Duplicate value for unique column 'email'
```

---

## DELETE

**Syntax:**

```sql
DELETE FROM table_name WHERE condition;
```

### Examples

**Delete specific row:**

```sql
DELETE FROM users WHERE id = 5;
```

**Delete multiple rows:**

```sql
DELETE FROM products WHERE price < 10;
```

**Delete all rows (dangerous!):**

```sql
DELETE FROM users;
-- Deletes EVERY row in the table
```

**Complex condition:**

```sql
DELETE FROM users WHERE age < 18 AND is_active = FALSE;
-- Note: AND is not yet supported, use single condition
```

### Notes

- WHERE clause is optional but recommended
- Without WHERE, deletes ALL rows
- Returns count of deleted rows
- Indexes are automatically rebuilt
- Cannot be undone

---

## Constraints

### PRIMARY KEY

**Purpose:** Uniquely identifies each row

**Features:**

- Must be unique
- Cannot be NULL
- Automatically indexed
- Only one per table

**Example:**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);
```

**Behavior:**

```sql
INSERT INTO users VALUES (1, 'John');  -- ✓ OK
INSERT INTO users VALUES (1, 'Jane');  -- ✗ Duplicate primary key
INSERT INTO users VALUES (NULL, 'Bob'); -- ✗ Primary key cannot be NULL
```

### UNIQUE

**Purpose:** Ensures all values in column are different

**Features:**

- All values must be unique
- NULL values allowed (not enforced yet)
- Automatically indexed
- Can have multiple per table

**Example:**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    username VARCHAR(50) UNIQUE
);
```

**Behavior:**

```sql
INSERT INTO users VALUES (1, 'john@example.com', 'john');  -- ✓ OK
INSERT INTO users VALUES (2, 'john@example.com', 'jane');  -- ✗ Duplicate email
INSERT INTO users VALUES (2, 'jane@example.com', 'john');  -- ✗ Duplicate username
INSERT INTO users VALUES (2, 'jane@example.com', 'jane');  -- ✓ OK
```

### NOT NULL

**Status:** Partially implemented

**Purpose:** Prevents NULL values

**Example:**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

**Note:** Currently parsed but not fully enforced.

---

## Operators

### Comparison Operators

| Operator     | Description           | Example             |
| ------------ | --------------------- | ------------------- |
| `=`          | Equal                 | `WHERE id = 1`      |
| `!=` or `<>` | Not equal             | `WHERE id != 5`     |
| `<`          | Less than             | `WHERE price < 100` |
| `>`          | Greater than          | `WHERE age > 18`    |
| `<=`         | Less than or equal    | `WHERE price <= 50` |
| `>=`         | Greater than or equal | `WHERE age >= 21`   |

### Examples

```sql
-- Numbers
SELECT * FROM products WHERE price > 10.00;
SELECT * FROM products WHERE price <= 50.00;
SELECT * FROM users WHERE age >= 18;

-- Strings (alphabetical comparison)
SELECT * FROM users WHERE name = 'John Doe';

-- Booleans
SELECT * FROM users WHERE is_active = TRUE;
SELECT * FROM users WHERE is_admin != FALSE;
```

### Logical Operators

**Status:** Not yet implemented

Future support planned for:

- `AND` - Both conditions true
- `OR` - Either condition true
- `NOT` - Negation

---

## Examples

### Complete Workflow

```sql
-- 1. Create schema
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    age INTEGER,
    is_active BOOLEAN
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR(200),
    content VARCHAR(1000)
);

-- 2. Insert data
INSERT INTO users VALUES (1, 'john_doe', 'john@example.com', 25, TRUE);
INSERT INTO users VALUES (2, 'jane_smith', 'jane@example.com', 30, TRUE);
INSERT INTO users VALUES (3, 'bob_jones', 'bob@example.com', 22, FALSE);

INSERT INTO posts VALUES (1, 1, 'My First Post', 'Hello World!');
INSERT INTO posts VALUES (2, 1, 'Second Post', 'More content here');
INSERT INTO posts VALUES (3, 2, 'Jane Post', 'Jane content');

-- 3. Query data
SELECT * FROM users;
SELECT username, email FROM users WHERE age > 24;
SELECT * FROM users WHERE is_active = TRUE;

-- 4. JOIN tables
SELECT users.username, posts.title
FROM users
JOIN posts ON users.id = posts.user_id;

-- 5. Update data
UPDATE users SET age = 26 WHERE id = 1;
UPDATE posts SET title = 'Updated Title' WHERE id = 1;

-- 6. Delete data
DELETE FROM posts WHERE id = 2;
DELETE FROM users WHERE is_active = FALSE;

-- 7. Drop tables
DROP TABLE posts;
DROP TABLE users;
```

### E-Commerce Example

```sql
-- Create tables
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    total FLOAT,
    shipped BOOLEAN
);

-- Insert data
INSERT INTO customers VALUES (1, 'Alice', 'alice@example.com');
INSERT INTO customers VALUES (2, 'Bob', 'bob@example.com');

INSERT INTO orders VALUES (1, 1, 99.99, TRUE);
INSERT INTO orders VALUES (2, 1, 149.99, FALSE);
INSERT INTO orders VALUES (3, 2, 79.99, TRUE);

-- Query orders with customer info
SELECT customers.name, orders.total, orders.shipped
FROM customers
JOIN orders ON customers.id = orders.customer_id;

-- Find unshipped orders
SELECT customers.name, customers.email, orders.total
FROM customers
JOIN orders ON customers.id = orders.customer_id
WHERE orders.shipped = FALSE;
```

---

## Limitations

Current SQL features NOT supported:

- `GROUP BY` and aggregates (`COUNT`, `SUM`, `AVG`)
- `ORDER BY` (partially implemented)
- `LIMIT` (partially implemented)
- Subqueries
- `UNION`, `INTERSECT`, `EXCEPT`
- `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN`
- `AND`, `OR` in WHERE clause
- `IN`, `BETWEEN`, `LIKE` operators
- `ALTER TABLE`
- `CREATE INDEX`
- Transactions (`BEGIN`, `COMMIT`, `ROLLBACK`)

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for planned features.

---

## Tips

1. **Always use PRIMARY KEY:**

   ```sql
   CREATE TABLE example (
       id INTEGER PRIMARY KEY,  -- Good
       ...
   );
   ```

2. **Use UNIQUE for emails, usernames:**

   ```sql
   email VARCHAR(100) UNIQUE  -- Prevents duplicates
   ```

3. **Be careful with UPDATE/DELETE without WHERE:**

   ```sql
   DELETE FROM users;  -- Deletes EVERYTHING!
   ```

4. **Test queries with SELECT first:**

   ```sql
   -- First see what will be affected
   SELECT * FROM users WHERE age < 18;

   -- Then delete if correct
   DELETE FROM users WHERE age < 18;
   ```

5. **Use meaningful column names:**

   ```sql
   -- Good
   created_at, updated_at, user_id

   -- Bad
   date1, date2, fk
   ```

---

## Next Steps

- Practice with [USAGE.md](USAGE.md)
- See architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
