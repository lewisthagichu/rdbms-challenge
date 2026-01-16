"""
Storage Layer - The Bottom Foundation
"""

from typing import Dict, List, Any, Optional
import json
import os


class StorageEngine:
    """
    The storage engine is responsible for:
    1. Storing table data in memory
    2. Providing CRUD operations at the storage level
    3. Optional: Persisting data to disk
    """

    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize the storage engine.

        Args:
            data_file: Optional path to persist data to disk
        """
        self.tables: Dict[str, List[Dict[str, Any]]] = {}
        self.data_file = data_file

        # Load existing data if file exists
        if data_file and os.path.exists(data_file):
            self.load_from_disk()

    def create_table(self, table_name: str) -> None:
        """Create a new table."""
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists")

        self.tables[table_name] = []
        self._save_to_disk()

    def drop_table(self, table_name: str) -> None:
        """Remove a table and all its data."""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")

        del self.tables[table_name]
        self._save_to_disk()

    def insert_row(self, table_name: str, row: Dict[str, Any]) -> None:
        """Insert a row into a table."""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")

        self.tables[table_name].append(row)
        self._save_to_disk()

    def get_all_rows(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get all rows from a table.

        Returns a copy to prevent external modification of our internal data.
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")

        return self.tables[table_name].copy()

    def update_rows(self, table_name: str, updated_rows: List[Dict[str, Any]]) -> None:
        """
        Replace all rows in a table.
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")

        self.tables[table_name] = updated_rows
        self._save_to_disk()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return table_name in self.tables

    def get_table_names(self) -> List[str]:
        """Get list of all table names."""
        return list(self.tables.keys())

    def _save_to_disk(self) -> None:
        """
        Persist data to disk as JSON.
        """
        if self.data_file:
            with open(self.data_file, 'w') as f:
                json.dump(self.tables, f, indent=2)

    def load_from_disk(self) -> None:
        """Load data from disk."""
        if self.data_file and os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.tables = json.load(f)
