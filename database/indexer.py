"""
Indexer module for managing indexes on database tables.
"""

from typing import Dict, Any, Optional, Set, List


class Index:
    """
    Represents a single index on a column.
    """

    def __init__(self, table_name: str, column_name: str, unique: bool = False):
        """
        Initialize an index.

        Args:
            table_name: Which table this index belongs to
            column_name: Which column is indexed
            unique: Whether values must be unique (primary keys, unique constraints)
        """
        self.table_name = table_name
        self.column_name = column_name
        self.unique = unique

        # The actual index: {column_value: row_index}
        # For unique indexes, one value maps to one row
        # For non-unique, one value could map to multiple rows
        self.index_map: Dict[Any, List[int]] = {}

    def build(self, rows: List[Dict[str, Any]]) -> None:
        """
        Build the index from scratch.

        Args:
            rows: All rows in the table
        """
        self.index_map.clear()

        for row_idx, row in enumerate(rows):
            value = row.get(self.column_name)
            if value is not None:  # Don't index NULL values
                self.add(value, row_idx)

    def add(self, value: Any, row_idx: int) -> None:
        """
        Add an entry to the index.
        """
        if value is None:
            return  # Don't index NULLs

        # Convert to hashable type (lists aren't hashable)
        if isinstance(value, list):
            value = tuple(value)

        if self.unique and value in self.index_map:
            raise ValueError(
                f"Duplicate value '{value}' violates unique constraint "
                f"on {self.table_name}.{self.column_name}"
            )

        if value not in self.index_map:
            self.index_map[value] = []

        self.index_map[value].append(row_idx)

    def remove(self, value: Any, row_idx: int) -> None:
        """Remove an entry from the index."""
        if value is None:
            return

        if isinstance(value, list):
            value = tuple(value)

        if value in self.index_map:
            if row_idx in self.index_map[value]:
                self.index_map[value].remove(row_idx)

            # Clean up empty entries
            if not self.index_map[value]:
                del self.index_map[value]

    def lookup(self, value: Any) -> List[int]:
        """
        Look up row indexes for a value.
        """
        if isinstance(value, list):
            value = tuple(value)

        return self.index_map.get(value, [])

    def get_all_values(self) -> Set[Any]:
        """Get all indexed values (useful for debugging)."""
        return set(self.index_map.keys())


class IndexManager:
    """
    Manages all indexes across all tables.
    """

    def __init__(self):
        # {table_name: {column_name: Index}}
        self.indexes: Dict[str, Dict[str, Index]] = {}

    def create_index(
        self,
        table_name: str,
        column_name: str,
        unique: bool = False
    ) -> Index:
        """Create a new index."""
        if table_name not in self.indexes:
            self.indexes[table_name] = {}

        if column_name in self.indexes[table_name]:
            raise ValueError(
                f"Index already exists on {table_name}.{column_name}"
            )

        index = Index(table_name, column_name, unique)
        self.indexes[table_name][column_name] = index
        return index

    def get_index(self, table_name: str, column_name: str) -> Optional[Index]:
        """Get an index if it exists."""
        return self.indexes.get(table_name, {}).get(column_name)

    def drop_table_indexes(self, table_name: str) -> None:
        """Remove all indexes for a table."""
        if table_name in self.indexes:
            del self.indexes[table_name]

    def rebuild_indexes(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """
        Rebuild all indexes for a table.
        """
        if table_name in self.indexes:
            for index in self.indexes[table_name].values():
                index.build(rows)
