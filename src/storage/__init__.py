"""Storage module for occupational reference data.

Provides SQLite database management with append-only temporal design
and full provenance tracking for DAMA-DMBOK 2.0 compliance.
"""

from .db_manager import get_connection, get_db, init_db, close_connection
from .repository import OccupationalGroupRepository

__all__ = [
    "get_connection",
    "get_db",
    "init_db",
    "close_connection",
    "OccupationalGroupRepository",
]
