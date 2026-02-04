"""Storage module for occupational reference data.

Provides SQLite database management with append-only temporal design
and full provenance tracking for DAMA-DMBOK 2.0 compliance.
"""

from .db_manager import get_connection, get_db, init_db, close_connection

# Lazy import to avoid circular dependencies
def __getattr__(name):
    if name == "OccupationalGroupRepository":
        from .repository import OccupationalGroupRepository
        return OccupationalGroupRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "get_connection",
    "get_db",
    "init_db",
    "close_connection",
    "OccupationalGroupRepository",
]
