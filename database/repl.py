"""
REPL - Read-Eval-Print Loop
"""

from database.storage import StorageEngine
from database.schema import SchemaManager
from database.indexer import IndexManager
from database.parser import SQLParser
from database.executor import QueryExecutor
from typing import Optional
import sys


class REPL:
    def __init__(self, data_file: Optional[str] = "database.json"):
        """
        Initialize the database components.

        Args:
            data_file: Path to persist data (None for no persistence)
        """
        print("Initializing database...")

        # Initialize all the core components
        self.storage = StorageEngine(data_file=data_file)
        self.schema_mgr = SchemaManager()
        self.index_mgr = IndexManager()
        self.parser = SQLParser()
        self.executor = QueryExecutor(
            self.storage, self.schema_mgr, self.index_mgr)

        print("Database initialized!")
        print()

    def start(self):
        """
        Start the REPL loop.

        This runs forever until the user types 'exit' or presses Ctrl+D.

        """
        self._print_welcome()

        while True:
            try:
                # Read a command from the user
                command = self._read_command()

                # Skip empty commands
                if not command or not command.strip():
                    continue

                # Check for special commands (start with backslash)
                if command.startswith('\\'):
                    self._handle_special_command(command)
                    continue

                # Check for exit commands
                if command.lower() in ('exit', 'quit'):
                    self._print_goodbye()
                    break

                # Execute as SQL
                self._execute_sql(command)

            except KeyboardInterrupt:
                # User pressed Ctrl+C
                print()
                print("Use 'exit' or '\\q' to quit, or Ctrl+D")
                continue

            except EOFError:
                # User pressed Ctrl+D
                print()
                self._print_goodbye()
                break

            except Exception as e:
                # Unexpected error - show it but don't crash
                print(f"Unexpected error: {str(e)}")
                continue

    def _read_command(self) -> str:
        """
        Read a SQL command from user input.

        Why multi-line? SQL commands can be long and span multiple lines.
        We read until we see a semicolon (;) which marks the end.

        Example:
          mydb> CREATE TABLE users (
             ->   id INTEGER,
             ->   name VARCHAR(100)
             -> );

        Returns:
            Complete SQL command (without the semicolon)
        """
        lines = []
        prompt = "mydb> "

        while True:
            try:
                # Read a line
                line = input(prompt)
                lines.append(line)

                # Check if command is complete (ends with semicolon)
                if line.strip().endswith(';'):
                    break

                # Continue reading - change prompt to show continuation
                prompt = "   -> "

            except EOFError:
                # User pressed Ctrl+D - propagate it up
                raise

        # Combine all lines into one command
        command = ' '.join(lines).strip()

        # Remove trailing semicolon
        if command.endswith(';'):
            command = command[:-1].strip()

        return command

    def _handle_special_command(self, command: str):
        r"""
        Handle special backslash commands.

        These are shortcuts that don't require SQL syntax.
        Similar to psql (PostgreSQL) commands.

        Supported commands:
        - \tables or \t       : List all tables
        - \describe <table>   : Show table structure
        - \d <table>          : Short for \describe
        - \help or \h or \?   : Show help
        - \q                  : Quit
        """
        parts = command.strip().split()
        cmd = parts[0].lower()

        if cmd in ('\\tables', '\\t'):
            self._list_tables()

        elif cmd in ('\\describe', '\\d'):
            if len(parts) < 2:
                print("Usage: \\describe <table_name>")
            else:
                self._describe_table(parts[1])

        elif cmd in ('\\help', '\\h', '\\?'):
            self._print_help()

        elif cmd == '\\q':
            self._print_goodbye()
            sys.exit(0)

        else:
            print(f"Unknown command: {cmd}")
            print("Type \\help for available commands")

        print()  # Blank line for readability

    def _execute_sql(self, sql: str):
        """
        Execute a SQL command and display results.

        Process:
        1. Parse the SQL into structured command
        2. Execute it
        3. Format and display results
        """
        try:
            # Parse SQL
            parsed = self.parser.parse(sql)

            # Execute
            result = self.executor.execute(parsed)

            # Display result
            if result['success']:
                # Success! Show a checkmark and message
                print(f"✓ {result['message']}")

                # If there's data (SELECT query), show it in a table
                if 'data' in result and result['data']:
                    self._display_table(result['data'], result.get('columns'))
            else:
                # Failed - show an X and error message
                print(f"✗ {result['message']}")

        except Exception as e:
            # Parsing or execution error
            print(f"✗ Error: {str(e)}")

        print()  # Blank line for readability

    def _display_table(self, rows: list, columns: Optional[list] = None):
        """
        Display query results in a nice ASCII table format.

        Example output:
          id | name     | email
          ----------------------------
          1  | John Doe | john@example.com
          2  | Jane Doe | jane@example.com

          (2 rows)

        Args:
            rows: List of row dictionaries
            columns: Optional list of column names (if None, use keys from first row)
        """
        if not rows:
            print("No rows returned.")
            return

        # Determine which columns to show
        if not columns:
            columns = list(rows[0].keys())

        # Calculate the width needed for each column
        # Start with column name length
        widths = {}
        for col in columns:
            widths[col] = len(str(col))

        # Check each row to find the widest value in each column
        for row in rows:
            for col in columns:
                value = str(row.get(col, ''))
                widths[col] = max(widths[col], len(value))

        # Print header row
        header_parts = []
        for col in columns:
            # Left-justify column name to its calculated width
            header_parts.append(col.ljust(widths[col]))
        print(" | ".join(header_parts))

        # Print separator line (dashes)
        total_width = sum(widths.values()) + 3 * (len(columns) - 1)
        print("-" * total_width)

        # Print data rows
        for row in rows:
            row_parts = []
            for col in columns:
                value = row.get(col, '')
                # Convert to string and left-justify
                row_parts.append(str(value).ljust(widths[col]))
            print(" | ".join(row_parts))

        # Print row count
        row_word = "row" if len(rows) == 1 else "rows"
        print(f"\n({len(rows)} {row_word})")

    def _list_tables(self):
        """
        List all tables in the database.

        Shows table name, row count, and column info.
        """
        tables = self.schema_mgr.get_all_table_names()

        if not tables:
            print("No tables in database.")
            print("Create a table with: CREATE TABLE ...")
        else:
            print("Tables in database:")
            print()
            for table in tables:
                schema = self.schema_mgr.get_schema(table)
                if not schema:
                    continue
                row_count = len(self.storage.get_all_rows(table))

                # Show table name and row count
                print(f"  📊 {table} ({row_count} rows)")

                # Show primary key if it exists
                if schema.primary_key:
                    print(f"      Primary Key: {schema.primary_key}")

                # Show number of columns
                print(f"      Columns: {len(schema.columns)}")
                print()

    def _describe_table(self, table_name: str):
        """
        Show detailed structure of a table.

        Displays:
        - Table name
        - All columns with types
        - Constraints (PRIMARY KEY, UNIQUE, NOT NULL)
        """
        schema = self.schema_mgr.get_schema(table_name)

        if not schema:
            print(f"Table '{table_name}' does not exist.")
            print(f"Use \\tables to see available tables.")
            return

        print(f"Table: {table_name}")
        print("=" * 60)
        print()
        print("Columns:")

        # Display each column
        for col in schema.columns:
            # Build type string (e.g., "VARCHAR(100)")
            type_str = col.data_type.value
            if col.max_length:
                type_str += f"({col.max_length})"

            # Collect constraints
            constraints = []
            if not col.nullable:
                constraints.append("NOT NULL")
            if col.name == schema.primary_key:
                constraints.append("PRIMARY KEY")
            if col.name in schema.unique_constraints and col.name != schema.primary_key:
                constraints.append("UNIQUE")

            # Build constraint string
            constraint_str = ""
            if constraints:
                constraint_str = " [" + ", ".join(constraints) + "]"

            # Print column info
            print(f"  • {col.name}: {type_str}{constraint_str}")

        # Show indexes
        if table_name in self.index_mgr.indexes:
            print()
            print("Indexes:")
            for col_name in self.index_mgr.indexes[table_name].keys():
                index = self.index_mgr.indexes[table_name][col_name]
                index_type = "UNIQUE" if index.unique else "INDEX"
                print(f"  • {col_name} ({index_type})")

        # Show row count
        row_count = len(self.storage.get_all_rows(table_name))
        print()
        print(f"Row count: {row_count}")

    def _print_welcome(self):
        """Print welcome message when REPL starts."""
        print("=" * 60)
        print("Welcome to MyDB - A Simple Relational Database")
        print("=" * 60)
        print()
        print("Type SQL commands followed by semicolon (;)")
        print("Special commands:")
        print("  \\tables          - List all tables")
        print("  \\describe <name> - Show table structure")
        print("  \\help            - Show help")
        print("  exit or \\q       - Exit")
        print()
        print("Example:")
        print("  mydb> CREATE TABLE users (id INTEGER PRIMARY KEY);")
        print()

    def _print_help(self):
        """Print help message."""
        print()
        print("=" * 60)
        print("MyDB Help")
        print("=" * 60)
        print()
        print("SPECIAL COMMANDS:")
        print("  \\tables, \\t              - List all tables")
        print("  \\describe <name>, \\d <name> - Show table structure")
        print("  \\help, \\h, \\?             - Show this help")
        print("  exit, quit, \\q            - Exit the database")
        print()
        print("SUPPORTED SQL:")
        print()
        print("CREATE TABLE:")
        print("  CREATE TABLE users (")
        print("    id INTEGER PRIMARY KEY,")
        print("    name VARCHAR(100),")
        print("    email VARCHAR(100) UNIQUE")
        print("  )")
        print()
        print("INSERT:")
        print("  INSERT INTO users VALUES (1, 'John', 'john@example.com')")
        print("  INSERT INTO users (name, email) VALUES ('Jane', 'jane@example.com')")
        print()
        print("SELECT:")
        print("  SELECT * FROM users")
        print("  SELECT name, email FROM users WHERE id = 1")
        print("  SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id")
        print()
        print("UPDATE:")
        print("  UPDATE users SET name = 'Jane Doe' WHERE id = 2")
        print()
        print("DELETE:")
        print("  DELETE FROM users WHERE id = 1")
        print()
        print("DROP TABLE:")
        print("  DROP TABLE users")
        print()
        print("DATA TYPES:")
        print("  INTEGER     - Whole numbers")
        print("  VARCHAR(n)  - Text up to n characters")
        print("  FLOAT       - Decimal numbers")
        print("  BOOLEAN     - True/False values")
        print()
        print("CONSTRAINTS:")
        print("  PRIMARY KEY - Unique identifier for rows")
        print("  UNIQUE      - Values must be unique")
        print("  NOT NULL    - Column cannot be null")
        print()

    def _print_goodbye(self):
        """Print goodbye message when exiting."""
        print()
        print("=" * 60)
        print("Thank you for using MyDB!")
        if self.storage.data_file:
            print(f"Your data has been saved to: {self.storage.data_file}")
        print("=" * 60)


def main():
    """
    Entry point for the REPL.

    """
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MyDB Interactive Shell')
    parser.add_argument(
        '--no-persist',
        action='store_true',
        help='Run in-memory only (no disk persistence)'
    )
    parser.add_argument(
        '--file',
        type=str,
        default='database.json',
        help='Database file path (default: database.json)'
    )

    args = parser.parse_args()

    # Determine data file
    data_file = None if args.no_persist else args.file

    # Create and start REPL
    repl = REPL(data_file=data_file)
    repl.start()


if __name__ == "__main__":
    main()
