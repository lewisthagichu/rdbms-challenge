"""
SQL Parser - The Translator
============================
Converts SQL text into structured Python objects we can work with.
"""

import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Parenthesis, Comparison, Token
from sqlparse.tokens import Keyword, DML, Whitespace, Punctuation, Number, String
from typing import Dict, List, Any, Optional, Tuple
import re


class SQLParser:
    """
    Parses SQL statements into structured commands.
    """

    def parse(self, sql: str) -> Dict[str, Any]:
        """
        Main entry point - parse any SQL statement.
        """
        # Parse the SQL (this creates a tree structure)
        parsed = sqlparse.parse(sql)

        if not parsed:
            raise ValueError("Empty SQL statement")

        statement = parsed[0]

        # Get the command type (SELECT, INSERT, etc.)
        command = self._get_command_type(statement)

        # Route to appropriate parser based on command
        if command == 'CREATE':
            return self._parse_create_table(statement)
        elif command == 'INSERT':
            return self._parse_insert(statement)
        elif command == 'SELECT':
            return self._parse_select(statement)
        elif command == 'UPDATE':
            return self._parse_update(statement)
        elif command == 'DELETE':
            return self._parse_delete(statement)
        elif command == 'DROP':
            return self._parse_drop(statement)
        else:
            raise ValueError(f"Unsupported command: {command}")

    def _get_command_type(self, statement) -> str:
        """
        Extract the command type (first keyword).

        Why iterate? sqlparse includes whitespace tokens, so we skip those.
        """
        for token in statement.tokens:
            if token.ttype in (DML, Keyword.DDL):
                return token.value.upper()
        raise ValueError("Could not determine command type")

    def _parse_create_table(self, statement) -> Dict[str, Any]:
        """
        Parse CREATE TABLE statements.

        Example:
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE
        )
        """
        tokens = [t for t in statement.tokens if not t.is_whitespace]

        # Find table name (after "TABLE" keyword)
        table_name = None
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'TABLE':
                if i + 1 < len(tokens):
                    table_name = self._extract_name(tokens[i + 1])
                break

        if not table_name:
            raise ValueError("Missing table name in CREATE TABLE")

        # Find column definitions (inside parentheses)
        columns = []
        primary_key = None
        unique_columns = []

        for token in tokens:
            if isinstance(token, Parenthesis):
                # Remove outer parentheses and split by commas
                column_defs = self._split_by_comma(token)

                for col_def in column_defs:
                    col_info = self._parse_column_definition(col_def)
                    columns.append(col_info)

                    if col_info.get('primary_key'):
                        primary_key = col_info['name']
                    if col_info.get('unique'):
                        unique_columns.append(col_info['name'])

        return {
            'command': 'CREATE_TABLE',
            'table': table_name,
            'columns': columns,
            'primary_key': primary_key,
            'unique_columns': unique_columns
        }

    def _parse_column_definition(self, col_def: str) -> Dict[str, Any]:
        """
        Parse a single column definition.

        Example: "id INTEGER PRIMARY KEY" or "name VARCHAR(100) UNIQUE"
        """
        parts = col_def.strip().split()

        if len(parts) < 2:
            raise ValueError(f"Invalid column definition: {col_def}")

        col_name = parts[0]
        col_type = parts[1].upper()

        # Extract VARCHAR length if present
        max_length = None
        if '(' in col_type:
            match = re.match(r'VARCHAR\((\d+)\)', col_type)
            if match:
                max_length = int(match.group(1))
                col_type = 'VARCHAR'

        # Check for constraints
        remaining = ' '.join(parts[2:]).upper()
        is_primary = 'PRIMARY KEY' in remaining
        is_unique = 'UNIQUE' in remaining
        is_nullable = 'NOT NULL' not in remaining

        return {
            'name': col_name,
            'type': col_type,
            'max_length': max_length,
            'nullable': is_nullable,
            'primary_key': is_primary,
            'unique': is_unique
        }

    def _parse_insert(self, statement) -> Dict[str, Any]:
        """
        Parse INSERT statements.

        Example:
        INSERT INTO users VALUES (1, 'John', 'john@example.com')
        INSERT INTO users (name, email) VALUES ('John', 'john@example.com')
        """
        tokens = [t for t in statement.tokens if not t.is_whitespace]

        # Find table name
        table_name = None
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'INTO':
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    table_name = self._extract_name(next_token)
                break

        if not table_name:
            raise ValueError("Missing table name in INSERT")

        # Find column names (if specified)
        columns = None
        for token in tokens:
            if isinstance(token, Parenthesis):
                # Check if this is column list or values list
                content = token.value[1:-1].strip()
                if not content.upper().startswith('SELECT') and ',' in content:
                    # Try to determine if it's a column list
                    first_item = content.split(',')[0].strip()
                    # If it's not a number or string literal, assume column names
                    if not (first_item.isdigit() or first_item.startswith("'")):
                        columns = [c.strip() for c in content.split(',')]
                        break

        # Find values
        values = []
        in_values = False
        for token in tokens:
            if token.ttype is Keyword and token.value.upper() == 'VALUES':
                in_values = True
                continue

            if in_values and isinstance(token, Parenthesis):
                # Extract values from parentheses
                content = token.value[1:-1].strip()
                values = self._parse_values(content)
                break

        if not values:
            raise ValueError("Missing VALUES in INSERT")

        return {
            'command': 'INSERT',
            'table': table_name,
            'columns': columns,
            'values': values
        }

    def _parse_select(self, statement) -> Dict[str, Any]:
        """
        Parse SELECT statements.

        Example:
        SELECT * FROM users
        SELECT name, email FROM users WHERE id = 5
        SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id
        """
        tokens = [t for t in statement.tokens if not t.is_whitespace]

        result = {
            'command': 'SELECT',
            'columns': [],
            'table': None,
            'where': None,
            'join': None,
            'order_by': None,
            'limit': None
        }

        # Find columns (between SELECT and FROM)
        for i, token in enumerate(tokens):
            if token.ttype is DML and token.value.upper() == 'SELECT':
                # Next token should be column list
                if i + 1 < len(tokens):
                    col_token = tokens[i + 1]
                    if col_token.value == '*':
                        result['columns'] = ['*']
                    elif isinstance(col_token, IdentifierList):
                        result['columns'] = [str(id).strip()
                                             for id in col_token.get_identifiers()]
                    elif isinstance(col_token, Identifier):
                        result['columns'] = [str(col_token).strip()]
                break

        # Find table name (after FROM)
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'FROM':
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    result['table'] = self._extract_name(next_token)
                break

        # Find WHERE clause
        for token in tokens:
            if isinstance(token, Where):
                result['where'] = self._parse_where(token)
                break

        # Find JOIN
        join_info = self._parse_join(statement)
        if join_info:
            result['join'] = join_info

        # Find ORDER BY
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'ORDER':
                if i + 1 < len(tokens) and tokens[i + 1].value.upper() == 'BY':
                    if i + 2 < len(tokens):
                        result['order_by'] = self._extract_name(tokens[i + 2])

        # Find LIMIT
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'LIMIT':
                if i + 1 < len(tokens):
                    try:
                        result['limit'] = int(tokens[i + 1].value)
                    except ValueError:
                        pass

        return result

    def _parse_update(self, statement) -> Dict[str, Any]:
        """
        Parse UPDATE statements.

        Example:
        UPDATE users SET name = 'Jane', email = 'jane@example.com' WHERE id = 1
        """
        tokens = [t for t in statement.tokens if not t.is_whitespace]

        # Find table name
        table_name = None
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'UPDATE':
                if i + 1 < len(tokens):
                    table_name = self._extract_name(tokens[i + 1])
                break

        if not table_name:
            raise ValueError("Missing table name in UPDATE")

        # Find SET clause
        updates = {}
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'SET':
                # Collect all comparison tokens until WHERE
                j = i + 1
                while j < len(tokens):
                    if tokens[j].ttype is Keyword and tokens[j].value.upper() == 'WHERE':
                        break

                    if isinstance(tokens[j], Comparison):
                        col, val = self._parse_comparison(tokens[j])
                        updates[col] = val

                    j += 1
                break

        # Find WHERE clause
        where = None
        for token in tokens:
            if isinstance(token, Where):
                where = self._parse_where(token)
                break

        return {
            'command': 'UPDATE',
            'table': table_name,
            'updates': updates,
            'where': where
        }

    def _parse_delete(self, statement) -> Dict[str, Any]:
        """
        Parse DELETE statements.

        Example:
        DELETE FROM users WHERE id = 5
        """
        tokens = [t for t in statement.tokens if not t.is_whitespace]

        # Find table name
        table_name = None
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'FROM':
                if i + 1 < len(tokens):
                    table_name = self._extract_name(tokens[i + 1])
                break

        if not table_name:
            raise ValueError("Missing table name in DELETE")

        # Find WHERE clause
        where = None
        for token in tokens:
            if isinstance(token, Where):
                where = self._parse_where(token)
                break

        return {
            'command': 'DELETE',
            'table': table_name,
            'where': where
        }

    def _parse_drop(self, statement) -> Dict[str, Any]:
        """Parse DROP TABLE statements."""
        tokens = [t for t in statement.tokens if not t.is_whitespace]

        table_name = None
        for i, token in enumerate(tokens):
            if token.ttype is Keyword and token.value.upper() == 'TABLE':
                if i + 1 < len(tokens):
                    table_name = self._extract_name(tokens[i + 1])
                break

        if not table_name:
            raise ValueError("Missing table name in DROP TABLE")

        return {
            'command': 'DROP_TABLE',
            'table': table_name
        }

    def _parse_where(self, where_token: Where) -> Dict[str, Any]:
        """
        Parse WHERE clause into conditions.

        Example: WHERE id = 5 AND name = 'John'
        """
        conditions = []

        # Find all comparisons in the WHERE clause
        for token in where_token.tokens:
            if isinstance(token, Comparison):
                col, val = self._parse_comparison(token)
                operator = self._extract_operator(token)
                conditions.append({
                    'column': col,
                    'operator': operator,
                    'value': val
                })

        if not conditions:
            raise ValueError("Empty WHERE clause")

        # For simplicity, we treat multiple conditions as AND
        if len(conditions) == 1:
            return conditions[0]
        else:
            return {'AND': conditions}

    def _parse_comparison(self, comp_token: Comparison) -> Tuple[str, Any]:
        """
        Parse a comparison like "id = 5" into ("id", 5).
        """
        parts = str(comp_token).split('=', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid comparison: {comp_token}")

        column = parts[0].strip()
        value_str = parts[1].strip()
        value = self._parse_value(value_str)

        return column, value

    def _extract_operator(self, comp_token: Comparison) -> str:
        """Extract comparison operator (=, >, <, etc.)."""
        comp_str = str(comp_token)

        if '>=' in comp_str:
            return '>='
        elif '<=' in comp_str:
            return '<='
        elif '>' in comp_str:
            return '>'
        elif '<' in comp_str:
            return '<'
        elif '=' in comp_str:
            return '='
        elif '!=' in comp_str or '<>' in comp_str:
            return '!='
        else:
            return '='

    def _parse_join(self, statement) -> Optional[Dict[str, Any]]:
        """
        Parse JOIN clause.

        Example: JOIN posts ON users.id = posts.user_id
        """
        tokens = [t for t in statement.tokens if not t.is_whitespace]

        join_table = None
        join_conditions = []

        for i, token in enumerate(tokens):
            if token.ttype is Keyword and 'JOIN' in token.value.upper():
                # Next token should be table name
                if i + 1 < len(tokens):
                    join_table = self._extract_name(tokens[i + 1])

                # Find ON clause
                for j in range(i + 2, len(tokens)):
                    if tokens[j].ttype is Keyword and tokens[j].value.upper() == 'ON':
                        # Parse join condition
                        if j + 1 < len(tokens):
                            if isinstance(tokens[j + 1], Comparison):
                                left, right = self._parse_join_condition(
                                    tokens[j + 1])
                                join_conditions.append({
                                    'left': left,
                                    'right': right
                                })
                        break
                break

        if join_table and join_conditions:
            return {
                'table': join_table,
                'conditions': join_conditions
            }

        return None

    def _parse_join_condition(self, comp_token: Comparison) -> Tuple[str, str]:
        """Parse join condition like 'users.id = posts.user_id'."""
        parts = str(comp_token).split('=')
        if len(parts) != 2:
            raise ValueError(f"Invalid join condition: {comp_token}")

        return parts[0].strip(), parts[1].strip()

    def _extract_name(self, token) -> str:
        """Extract a clean name from a token (removes quotes, whitespace)."""
        if isinstance(token, Identifier):
            return str(token.get_name())
        else:
            return str(token).strip().strip('"').strip("'")

    def _parse_value(self, value_str: str) -> Any:
        """
        Convert a string value to appropriate Python type.

        '5' -> 5 (int)
        '3.14' -> 3.14 (float)
        "'hello'" -> 'hello' (str)
        'TRUE' -> True (bool)
        """
        value_str = value_str.strip()

        # String literal
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]

        # Boolean
        if value_str.upper() in ('TRUE', 'FALSE'):
            return value_str.upper() == 'TRUE'

        # NULL
        if value_str.upper() == 'NULL':
            return None

        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            # If not a number, treat as string
            return value_str

    def _parse_values(self, values_str: str) -> List[Any]:
        """Parse comma-separated values."""
        values = []
        for val in values_str.split(','):
            values.append(self._parse_value(val.strip()))
        return values

    def _split_by_comma(self, token: Parenthesis) -> List[str]:
        """Split parenthesis content by commas."""
        content = token.value[1:-1]  # Remove outer parentheses
        return [s.strip() for s in content.split(',')]
