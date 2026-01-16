# MyDB Documentation

Complete documentation for the MyDB Relational Database Management System.

---

## 📚 Documentation Index

### Getting Started

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Installation, setup, and first steps
  - Prerequisites
  - Virtual environment setup
  - Running the REPL, API, and web interface
  - Troubleshooting common issues

### User Guides

- **[USAGE.md](USAGE.md)** - How to use all three interfaces

  - REPL (Command Line) guide
  - REST API reference
  - Web interface walkthrough
  - Common workflows and examples

- **[SQL_REFERENCE.md](SQL_REFERENCE.md)** - Complete SQL command documentation
  - Data types (INTEGER, VARCHAR, FLOAT, BOOLEAN)
  - All supported commands (CREATE, INSERT, SELECT, UPDATE, DELETE)
  - Constraints (PRIMARY KEY, UNIQUE)
  - Operators and examples

### Technical Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and components

  - High-level architecture
  - Component breakdown
  - Data flow examples
  - Performance characteristics

- **[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)** - Why things are built this way

  - In-memory storage rationale
  - Hash indexes vs B-trees
  - Nested loop JOIN explanation
  - Trade-offs and alternatives

- **[API_REFERENCE.md](API_REFERENCE.md)** - REST API documentation
  - All endpoints
  - Request/response formats
  - cURL examples
  - Error handling

### Development Resources

- **[RESOURCES.md](RESOURCES.md)** - Books, courses, and tutorials used

  - Recommended learning materials
  - Helpful documentation
  - Community resources

- **[CREDITS.md](CREDITS.md)** - Complete attribution
  - Libraries and dependencies
  - AI assistance disclosure
  - Learning resources
  - Acknowledgments

---

## 📖 Quick Reference

### Common Tasks

**Install and run:**

```bash
# See GETTING_STARTED.md
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m database.repl
```

**SQL syntax:**

```sql
-- See SQL_REFERENCE.md
CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(100));
INSERT INTO users VALUES (1, 'John');
SELECT * FROM users;
```

**API calls:**

```bash
# See API_REFERENCE.md
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users"}'
```

---

## 🎯 Documentation Goals

This documentation aims to:

1. **Enable Quick Start**: Get users up and running in minutes
2. **Teach Concepts**: Explain database internals, not just usage
3. **Show Trade-offs**: Be honest about limitations and alternatives
4. **Provide Examples**: Every feature has working code examples
5. **Encourage Learning**: Link to resources for deeper understanding

---

## 📬 Questions?

If you can't find what you're looking for:

1. **Check the relevant doc** - Use the index above
2. **Search this folder** - Use your text editor's search
3. **Check the code** - It's heavily commented
4. **Open an issue** - Ask on GitHub

---

## 📜 License

All documentation is released under MIT License, same as the code.

Feel free to use, modify, and share!
