# Getting Started with MyDB

This guide will help you set up and run MyDB on your local machine.

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **Python 3.8 or higher**

  - Check: `python3 --version`
  - Download: https://www.python.org/downloads/

- **pip** (Python package manager)
  - Usually comes with Python
  - Check: `pip --version`

### Optional (for Web Interface)

- **Node.js 16 or higher**

  - Check: `node --version`
  - Download: https://nodejs.org/

- **npm** (Node package manager)
  - Comes with Node.js
  - Check: `npm --version`

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/lewisthagichu/rdbms-challenge.git
cd rdbms-challenge
```

### Step 2: Set Up Python Environment

#### Create Virtual Environment

**Why use a virtual environment?**

- Isolates project dependencies
- Prevents conflicts with system Python
- Makes deployment easier

**On Linux/Mac:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your prompt
```

**On Windows (Command Prompt):**

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat
```

**On Windows (PowerShell):**

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1

# If you get an error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**

- `fastapi==0.104.1` - Web framework for REST API
- `uvicorn==0.24.0` - ASGI server
- `sqlparse==0.4.4` - SQL parsing
- `pydantic==2.5.0` - Data validation
- `python-multipart==0.0.6` - Form data handling

**Verify installation:**

```bash
pip list
```

You should see all packages listed.

### Step 3: Set Up Frontend (Optional)

Only needed if you want to use the web interface.

```bash
cd frontend
npm install
cd ..
```

**What gets installed:**

- React and dependencies
- Vite (build tool)
- Development server

---

## Verify Installation

### Test the REPL

```bash
python3 -m database.repl
```

You should see:

```
Initializing database...
Database initialized!

============================================================
Welcome to MyDB - A Simple Relational Database
============================================================

Type SQL commands followed by semicolon (;)
Special commands:
  \tables          - List all tables
  \describe <name> - Show table structure
  \help            - Show help
  exit or \q       - Exit

mydb>
```

Try a simple command:

```sql
mydb> CREATE TABLE test (id INTEGER PRIMARY KEY);
✓ Table 'test' created successfully

mydb> \tables
Tables in database:

  📊 test (0 rows)
      Primary Key: id
      Columns: 1

mydb> exit
```

### Test the API

**Start the server:**

```bash
uvicorn api.main:app --port 8001
```

You should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Test it (in another terminal):**

```bash
curl http://localhost:8001/
```

Response:

```json
{
  "message": "MyDB API is running",
  "version": "1.0.0"
}
```

### Test the Frontend

**Terminal 1 - Start API:**

```bash
uvicorn api.main:app --port 8001
```

**Terminal 2 - Start Frontend:**

```bash
cd frontend
npm run dev
```

You should see:

```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Open browser to:** `http://localhost:5173`

You should see the MyDB web interface.

---

## Common Issues & Solutions

### Issue: "python3: command not found"

**Solution:**

- On Windows, try `python` instead of `python3`
- Or install Python from https://www.python.org/

### Issue: "externally-managed-environment" error

**Solution:**

- You're not in a virtual environment
- Follow Step 2 to create and activate venv

### Issue: Virtual environment not activating

**Solution (Windows PowerShell):**

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Port 8001 already in use

**Solution:**

```bash
# Find what's using port 8001
lsof -i :8001  # Mac/Linux
netstat -ano | findstr :8001  # Windows

# Kill the process or use different port
uvicorn api.main:app --port 8002
```

### Issue: "Module not found" errors

**Solution:**

```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Frontend won't start

**Solution:**

```bash
# Clear npm cache
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: CORS errors in browser

**Solution:**

- Make sure API is running on port 8001
- Check `api/main.py` has correct CORS origins
- Try hard refresh (Ctrl+F5)

---

## Development Workflow

### Daily Workflow

1. **Activate virtual environment:**

   ```bash
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Start working:**

   ```bash
   # Option 1: REPL
   python3 -m database.repl

   # Option 2: API
   python3 api/main.py

   # Option 3: Web app (2 terminals)
   python3 api/main.py        # Terminal 1
   cd frontend && npm run dev # Terminal 2
   ```

3. **When done:**
   ```bash
   deactivate  # Exit virtual environment
   ```

### File Locations

**Database files:**

- REPL: `database.json`
- API: `api_database.json`

**These are created automatically and persist data between runs.**

To start fresh:

```bash
rm database.json api_database.json
```

---

## Next Steps

Now that you have MyDB running:

1. **Learn the basics:** Read [USAGE.md](USAGE.md)
2. **Try SQL commands:** See [SQL_REFERENCE.md](SQL_REFERENCE.md)
3. **Understand the architecture:** Read [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Explore the code:** Start with `database/storage.py`

---

## Quick Command Reference

```bash
# Virtual Environment
python3 -m venv venv              # Create
source venv/bin/activate          # Activate (Mac/Linux)
venv\Scripts\activate             # Activate (Windows)
deactivate                        # Deactivate

# Installation
pip install -r requirements.txt   # Install Python deps
cd frontend && npm install        # Install Node deps

# Run
python3 -m database.repl          # REPL
uvicorn api.main:app --port 8001              # API
cd frontend && npm run dev        # Frontend

# Cleanup
rm database.json                  # Delete DB file
rm -rf venv                       # Remove virtual env
rm -rf frontend/node_modules      # Remove Node modules
```
