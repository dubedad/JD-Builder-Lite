"""Database connection manager for occupational reference data.

Provides SQLite connection management with WAL mode for concurrent reads,
foreign key enforcement, and context manager pattern.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# Database and schema paths (relative to project root)
DB_PATH = Path("data/occupational.db")
SCHEMA_PATH = Path("src/storage/schema.sql")


def get_connection() -> sqlite3.Connection:
    """Create a new database connection with proper configuration.

    Returns:
        sqlite3.Connection configured with:
        - row_factory = sqlite3.Row (dict-like access)
        - PRAGMA foreign_keys = ON (enforce FKs)
        - PRAGMA journal_mode = WAL (concurrent reads)
        - PRAGMA busy_timeout = 5000 (5 second wait on lock)
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Create connection
    conn = sqlite3.connect(str(DB_PATH))

    # Enable dict-like row access
    conn.row_factory = sqlite3.Row

    # Configure pragmas
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")

    return conn


def init_db() -> sqlite3.Connection:
    """Initialize the database with schema.

    Creates all tables, indexes, and views from schema.sql.
    Safe to call multiple times (uses IF NOT EXISTS).

    Returns:
        sqlite3.Connection for chaining operations
    """
    conn = get_connection()

    # Read and execute schema
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()

    return conn


def close_connection(conn: Optional[sqlite3.Connection]) -> None:
    """Safely close a database connection.

    Args:
        conn: Connection to close, or None (no-op)
    """
    if conn is not None:
        conn.close()


@contextmanager
def get_db():
    """Context manager for database connections.

    Ensures connection is properly closed after use.

    Usage:
        with get_db() as conn:
            cursor = conn.execute("SELECT ...")

    Yields:
        sqlite3.Connection with proper configuration
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
