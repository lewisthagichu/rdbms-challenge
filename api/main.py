"""
FastAPI Backend
===============
REST API for our database system.

Endpoints:
- POST /query - Execute a SQL query
- GET /tables - List all tables
- GET /tables/{name} - Get table schema and data
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from database.storage import StorageEngine
from database.schema import SchemaManager
from database.indexer import IndexManager
from database.parser import SQLParser
from database.executor import QueryExecutor
import sys
import os
# Add parent directory to path so we can import database modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Pydantic models for request/response validation
class QueryRequest(BaseModel):
    """Request model for SQL queries."""
    sql: str


class QueryResponse(BaseModel):
    """Response model for query results."""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None


class TableInfo(BaseModel):
    """Information about a table."""
    name: str
    row_count: int
    columns: List[Dict[str, str]]


# Initialize FastAPI app
app = FastAPI(
    title="MyDB API",
    description="REST API for a simple relational database",
    version="1.0.0"
)

# Configure CORS to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database components (single instance for all requests)
storage = StorageEngine(data_file="api_database.json")
schema_mgr = SchemaManager()
index_mgr = IndexManager()
parser = SQLParser()
executor = QueryExecutor(storage, schema_mgr, index_mgr)


@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {
        "message": "MyDB API is running",
        "version": "1.0.0",
        "endpoints": [
            "/query",
            "/tables",
            "/tables/{name}"
        ]
    }


@app.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute a SQL query."""
    try:
        # Parse SQL
        parsed = parser.parse(request.sql)

        # Execute
        result = executor.execute(parsed)

        return QueryResponse(**result)

    except Exception as e:
        # Return error as unsuccessful query result
        return QueryResponse(
            success=False,
            message=str(e)
        )


@app.get("/tables")
async def list_tables():
    """
    List all tables in the database.

    Returns table names, row counts, and column info.
    """
    tables = []

    for table_name in schema_mgr.get_all_table_names():
        schema = schema_mgr.get_schema(table_name)
        if not schema:
            # Skip entries without a valid schema to avoid attribute access on None
            continue
        rows = storage.get_all_rows(table_name)

        columns = []
        for col in schema.columns:
            col_info = {
                "name": col.name,
                "type": col.data_type.value,
                "nullable": col.nullable
            }
            if col.max_length:
                col_info["max_length"] = col.max_length
            columns.append(col_info)

        tables.append({
            "name": table_name,
            "row_count": len(rows),
            "columns": columns,
            "primary_key": schema.primary_key,
            "unique_constraints": list(schema.unique_constraints)
        })

    return {"tables": tables}


@app.get("/tables/{table_name}")
async def get_table(table_name: str):
    """
    Get detailed information about a specific table.

    Returns schema and all data.
    """
    schema = schema_mgr.get_schema(table_name)

    if not schema:
        raise HTTPException(
            status_code=404, detail=f"Table '{table_name}' not found")

    rows = storage.get_all_rows(table_name)

    columns = []
    for col in schema.columns:
        col_info = {
            "name": col.name,
            "type": col.data_type.value,
            "nullable": col.nullable
        }
        if col.max_length:
            col_info["max_length"] = col.max_length
        columns.append(col_info)

    return {
        "name": table_name,
        "columns": columns,
        "primary_key": schema.primary_key,
        "unique_constraints": list(schema.unique_constraints),
        "row_count": len(rows),
        "data": rows
    }


@app.delete("/tables/{table_name}")
async def drop_table(table_name: str):
    """
    Drop a table.

    Why DELETE method? RESTful convention for deleting resources.
    """
    if not schema_mgr.table_exists(table_name):
        raise HTTPException(
            status_code=404, detail=f"Table '{table_name}' not found")

    schema_mgr.drop_schema(table_name)
    storage.drop_table(table_name)
    index_mgr.drop_table_indexes(table_name)

    return {"message": f"Table '{table_name}' dropped successfully"}


if __name__ == "__main__":
    import uvicorn

    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8001)
