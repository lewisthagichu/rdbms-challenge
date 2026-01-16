"""
Schema Manager - The Blueprint
===============================
This module manages table definitions (metadata).


A schema defines:
- Table name
- Columns (name, data type)
- Primary key
- Unique constraints
- Indexes
"""

from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field


class DataType(Enum):
    """
    Supported data types.
    """
    INTEGER = "INTEGER"
    VARCHAR = "VARCHAR"
    BOOLEAN = "BOOLEAN"
    FLOAT = "FLOAT"


@dataclass
class Column:
    """
    Represents a column definition.
    """
    name: str
    data_type: DataType
    max_length: Optional[int] = None  # For VARCHAR(n)
    nullable: bool = True

    def validate_value(self, value: Any) -> Any:
        """
        Validate and convert a value to the correct type.
        """
        if value is None:
            if not self.nullable:
                raise ValueError(f"Column '{self.name}' cannot be NULL")
            return None

        # Type checking and conversion
        if self.data_type == DataType.INTEGER:
            if not isinstance(value, int):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot convert '{value}' to INTEGER")
            return value

        elif self.data_type == DataType.FLOAT:
            if not isinstance(value, (int, float)):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot convert '{value}' to FLOAT")
            return float(value)

        elif self.data_type == DataType.VARCHAR:
            value_str = str(value)
            if self.max_length and len(value_str) > self.max_length:
                raise ValueError(
                    f"Value '{value_str}' exceeds max length {self.max_length}"
                )
            return value_str

        elif self.data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ('true', '1', 'yes'):
                    return True
                if value.lower() in ('false', '0', 'no'):
                    return False
            raise ValueError(f"Cannot convert '{value}' to BOOLEAN")

        return value


@dataclass
class TableSchema:
    """
    Represents the complete definition of a table.
    """
    name: str
    columns: List[Column]
    primary_key: Optional[str] = None
    unique_constraints: Set[str] = field(default_factory=set)
    indexes: Set[str] = field(default_factory=set)

    def get_column(self, column_name: str) -> Optional[Column]:
        """Find a column by name."""
        for col in self.columns:
            if col.name == column_name:
                return col
        return None

    def validate_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a row against this schema.

        This ensures:
        1. All required columns are present
        2. No extra columns exist
        3. Values match their data types
        4. VARCHAR lengths are respected
        """
        validated_row = {}

        # Check all columns
        for column in self.columns:
            if column.name not in row:
                if not column.nullable:
                    raise ValueError(f"Missing required column: {column.name}")
                validated_row[column.name] = None
            else:
                validated_row[column.name] = column.validate_value(
                    row[column.name])

        # Check for extra columns
        for key in row:
            if not self.get_column(key):
                raise ValueError(f"Unknown column: {key}")

        return validated_row

    def get_column_names(self) -> List[str]:
        """Get list of all column names."""
        return [col.name for col in self.columns]


class SchemaManager:
    """
    Manages all table schemas in the database.
    """

    def __init__(self):
        self.schemas: Dict[str, TableSchema] = {}

    def create_table_schema(
        self,
        table_name: str,
        columns: List[Column],
        primary_key: Optional[str] = None,
        unique_constraints: Optional[List[str]] = None
    ) -> TableSchema:
        """
        Create a new table schema.
        """
        if table_name in self.schemas:
            raise ValueError(f"Table schema '{table_name}' already exists")

        # Validate primary key exists as a column
        if primary_key:
            if not any(col.name == primary_key for col in columns):
                raise ValueError(
                    f"Primary key '{primary_key}' is not a column")

        # Validate unique constraints
        if unique_constraints:
            for uc in unique_constraints:
                if not any(col.name == uc for col in columns):
                    raise ValueError(
                        f"Unique constraint '{uc}' is not a column")

        schema = TableSchema(
            name=table_name,
            columns=columns,
            primary_key=primary_key,
            unique_constraints=set(unique_constraints or []),
            indexes=set()
        )

        # Primary keys automatically get an index
        if primary_key:
            schema.indexes.add(primary_key)

        self.schemas[table_name] = schema
        return schema

    def get_schema(self, table_name: str) -> Optional[TableSchema]:
        """Get schema for a table."""
        return self.schemas.get(table_name)

    def drop_schema(self, table_name: str) -> None:
        """Remove a table schema."""
        if table_name in self.schemas:
            del self.schemas[table_name]

    def table_exists(self, table_name: str) -> bool:
        """Check if a table schema exists."""
        return table_name in self.schemas

    def get_all_table_names(self) -> List[str]:
        """Get all table names."""
        return list(self.schemas.keys())
