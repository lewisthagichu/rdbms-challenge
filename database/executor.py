"""
Query Executor - Takes parsed SQL commands and executes them.
"""

from typing import Dict, List, Any, Optional
from database.storage import StorageEngine
from database.schema import SchemaManager, Column, DataType, TableSchema
from database.indexer import IndexManager


class QueryExecutor:
    """
    Executes parsed SQL commands.
    """

    def __init__(self, storage: StorageEngine, schema_mgr: SchemaManager, index_mgr: IndexManager):
        """
        Initialize with our three core components.
        """
        self.storage = storage
        self.schema_mgr = schema_mgr
        self.index_mgr = index_mgr

    def execute(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point
        """
        command = parsed_query['command']

        try:
            if command == 'CREATE_TABLE':
                return self._execute_create_table(parsed_query)
            elif command == 'DROP_TABLE':
                return self._execute_drop_table(parsed_query)
            elif command == 'INSERT':
                return self._execute_insert(parsed_query)
            elif command == 'SELECT':
                return self._execute_select(parsed_query)
            elif command == 'UPDATE':
                return self._execute_update(parsed_query)
            elif command == 'DELETE':
                return self._execute_delete(parsed_query)
            else:
                return {
                    'success': False,
                    'message': f"Unknown command: {command}"
                }

        except Exception as e:
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }

    def _execute_create_table(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute CREATE TABLE.

        Steps:
        1. Create schema (metadata)
        2. Create storage (actual table)
        3. Create indexes for primary key and unique columns
        """
        table_name = parsed['table']

        # Convert parsed columns to Column objects
        columns = []
        for col_info in parsed['columns']:
            data_type = DataType[col_info['type']]
            column = Column(
                name=col_info['name'],
                data_type=data_type,
                max_length=col_info.get('max_length'),
                nullable=col_info.get('nullable', True)
            )
            columns.append(column)

        # Create schema
        schema = self.schema_mgr.create_table_schema(
            table_name=table_name,
            columns=columns,
            primary_key=parsed.get('primary_key'),
            unique_constraints=parsed.get('unique_columns', [])
        )

        # Create storage
        self.storage.create_table(table_name)

        # Create indexes for primary key and unique columns
        if schema.primary_key:
            self.index_mgr.create_index(
                table_name, schema.primary_key, unique=True)

        for unique_col in schema.unique_constraints:
            if unique_col != schema.primary_key:  # Don't duplicate PK index
                self.index_mgr.create_index(
                    table_name, unique_col, unique=True)

        return {
            'success': True,
            'message': f"Table '{table_name}' created successfully"
        }

    def _execute_drop_table(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute DROP TABLE.

        Clean up schema, storage, and indexes.
        """
        table_name = parsed['table']

        if not self.schema_mgr.table_exists(table_name):
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }

        self.schema_mgr.drop_schema(table_name)
        self.storage.drop_table(table_name)
        self.index_mgr.drop_table_indexes(table_name)

        return {
            'success': True,
            'message': f"Table '{table_name}' dropped successfully"
        }

    def _execute_insert(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute INSERT.

        Steps:
        1. Get schema
        2. Build row dict from values
        3. Validate against schema
        4. Check unique constraints via indexes
        5. Insert into storage
        6. Update indexes
        """
        table_name = parsed['table']

        schema = self.schema_mgr.get_schema(table_name)
        if not schema:
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }

        # Build row dict
        if parsed['columns']:
            # Columns specified: INSERT INTO users (name, email) VALUES (...)
            if len(parsed['columns']) != len(parsed['values']):
                return {
                    'success': False,
                    'message': "Column count doesn't match value count"
                }
            row = dict(zip(parsed['columns'], parsed['values']))
        else:
            # No columns specified: INSERT INTO users VALUES (...)
            # Values must match column order in schema
            if len(parsed['values']) != len(schema.columns):
                return {
                    'success': False,
                    'message': f"Expected {len(schema.columns)} values, got {len(parsed['values'])}"
                }
            row = dict(zip(schema.get_column_names(), parsed['values']))

        # Validate row against schema
        try:
            validated_row = schema.validate_row(row)
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }

        # Check unique constraints using indexes
        for col_name in schema.unique_constraints:
            index = self.index_mgr.get_index(table_name, col_name)
            if index:
                value = validated_row.get(col_name)
                if value is not None and index.lookup(value):
                    return {
                        'success': False,
                        'message': f"Duplicate value '{value}' for unique column '{col_name}'"
                    }

        # Check primary key
        if schema.primary_key:
            pk_index = self.index_mgr.get_index(table_name, schema.primary_key)
            if pk_index:
                pk_value = validated_row.get(schema.primary_key)
                if pk_value is not None and pk_index.lookup(pk_value):
                    return {
                        'success': False,
                        'message': f"Duplicate primary key value: {pk_value}"
                    }

        # Insert into storage
        self.storage.insert_row(table_name, validated_row)

        # Update indexes
        rows = self.storage.get_all_rows(table_name)
        row_idx = len(rows) - 1  # Just inserted, so it's the last one

        # Update all indexes for this table
        if table_name in self.index_mgr.indexes:
            for col_name, index in self.index_mgr.indexes[table_name].items():
                value = validated_row.get(col_name)
                if value is not None:
                    index.add(value, row_idx)

        return {
            'success': True,
            'message': f"Row inserted into '{table_name}'"
        }

    def _execute_select(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SELECT.

        Steps:
        1. Get all rows from storage
        2. Apply WHERE filter
        3. Apply JOIN if present
        4. Select requested columns
        5. Apply ORDER BY
        6. Apply LIMIT
        """
        table_name = parsed['table']

        schema = self.schema_mgr.get_schema(table_name)
        if not schema:
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }

        # Get rows
        rows = self.storage.get_all_rows(table_name)

        # Apply WHERE clause
        if parsed['where']:
            rows = self._apply_where(rows, parsed['where'], schema)

        # Apply JOIN
        if parsed['join']:
            rows = self._apply_join(rows, parsed['join'], table_name)

        # Select columns
        if parsed['columns'] == ['*']:
            result_rows = rows
        else:
            result_rows = []
            for row in rows:
                result_row = {}
                for col in parsed['columns']:
                    # Handle table.column notation
                    if '.' in col:
                        result_row[col] = row.get(col)
                    else:
                        result_row[col] = row.get(col)
                result_rows.append(result_row)

        # Apply ORDER BY (simple implementation)
        if parsed['order_by']:
            try:
                result_rows.sort(key=lambda x: x.get(parsed['order_by'], ''))
            except Exception:
                pass  # Silently skip if can't sort

        # Apply LIMIT
        if parsed['limit']:
            result_rows = result_rows[:parsed['limit']]

        return {
            'success': True,
            'message': f"Found {len(result_rows)} row(s)",
            'data': result_rows,
            'columns': parsed['columns'] if parsed['columns'] != ['*'] else schema.get_column_names()
        }

    def _execute_update(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute UPDATE.

        Steps:
        1. Get all rows
        2. Filter by WHERE
        3. Update matching rows
        4. Validate updates
        5. Save back to storage
        6. Rebuild indexes
        """
        table_name = parsed['table']

        schema = self.schema_mgr.get_schema(table_name)
        if not schema:
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }

        rows = self.storage.get_all_rows(table_name)
        updated_count = 0

        # Update matching rows
        for i, row in enumerate(rows):
            if not parsed['where'] or self._row_matches_where(row, parsed['where'], schema):
                # Apply updates
                for col, val in parsed['updates'].items():
                    row[col] = val

                # Validate updated row
                try:
                    rows[i] = schema.validate_row(row)
                    updated_count += 1
                except ValueError as e:
                    return {
                        'success': False,
                        'message': f"Validation error: {str(e)}"
                    }

        # Save updated rows
        self.storage.update_rows(table_name, rows)

        # Rebuild indexes
        self.index_mgr.rebuild_indexes(table_name, rows)

        return {
            'success': True,
            'message': f"Updated {updated_count} row(s)"
        }

    def _execute_delete(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute DELETE.

        Steps:
        1. Get all rows
        2. Filter out rows matching WHERE
        3. Save remaining rows
        4. Rebuild indexes
        """
        table_name = parsed['table']

        schema = self.schema_mgr.get_schema(table_name)
        if not schema:
            return {
                'success': False,
                'message': f"Table '{table_name}' does not exist"
            }

        rows = self.storage.get_all_rows(table_name)
        original_count = len(rows)

        # Filter out rows to delete
        if parsed['where']:
            rows = [row for row in rows if not self._row_matches_where(
                row, parsed['where'], schema)]
        else:
            # No WHERE clause = delete all rows
            rows = []

        deleted_count = original_count - len(rows)

        # Save remaining rows
        self.storage.update_rows(table_name, rows)

        # Rebuild indexes
        self.index_mgr.rebuild_indexes(table_name, rows)

        return {
            'success': True,
            'message': f"Deleted {deleted_count} row(s)"
        }

    def _apply_where(self, rows: List[Dict[str, Any]], where: Dict[str, Any], schema: TableSchema) -> List[Dict[str, Any]]:
        """
        Filter rows based on WHERE clause.
        """
        return [row for row in rows if self._row_matches_where(row, where, schema)]

    def _row_matches_where(self, row: Dict[str, Any], where: Dict[str, Any], schema: TableSchema) -> bool:
        """
        Check if a row matches WHERE conditions.

        Supports simple conditions and AND.
        """
        if 'AND' in where:
            # Multiple conditions - all must match
            return all(self._row_matches_where(row, cond, schema) for cond in where['AND'])

        # Single condition
        column = where['column']
        operator = where['operator']
        expected = where['value']
        actual = row.get(column)

        # Comparison
        if operator == '=':
            return actual == expected
        elif operator == '!=':
            return actual != expected
        elif operator == '>':
            return actual > expected
        elif operator == '<':
            return actual < expected
        elif operator == '>=':
            return actual >= expected
        elif operator == '<=':
            return actual <= expected
        else:
            return False

    def _apply_join(self, left_rows: List[Dict[str, Any]], join_info: Dict[str, Any], left_table: str) -> List[Dict[str, Any]]:
        """
        Perform a JOIN operation.
        """
        right_table = join_info['table']
        conditions = join_info['conditions']

        # Get right table data
        right_rows = self.storage.get_all_rows(right_table)

        result = []

        for left_row in left_rows:
            for right_row in right_rows:
                # Check join conditions
                match = True
                for cond in conditions:
                    left_col = cond['left']
                    right_col = cond['right']

                    # Extract table.column
                    left_val = self._extract_join_value(
                        left_row, left_col, left_table)
                    right_val = self._extract_join_value(
                        right_row, right_col, right_table)

                    if left_val != right_val:
                        match = False
                        break

                if match:
                    # Combine rows with table prefixes
                    combined = {}
                    for k, v in left_row.items():
                        combined[f"{left_table}.{k}"] = v
                    for k, v in right_row.items():
                        combined[f"{right_table}.{k}"] = v
                    result.append(combined)

        return result

    def _extract_join_value(self, row: Dict[str, Any], col_ref: str, table_name: str) -> Any:
        """Extract value for join comparison, handling table.column notation."""
        if '.' in col_ref:
            # table.column notation
            parts = col_ref.split('.')
            if len(parts) == 2:
                return row.get(parts[1])
        else:
            # Just column name
            return row.get(col_ref)

        return None
