"""Parquet data models for JobForge 2.0 integration."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, Optional, TypeVar


class CoverageStatus(str, Enum):
    """Three-state result for parquet file lookups.

    Distinguishes between:
    - LOAD_ERROR: file missing, corrupt, or unreadable
    - NOT_FOUND: file loaded but no rows match the lookup key
    - FOUND: file loaded and matching rows returned
    """

    LOAD_ERROR = "load_error"
    NOT_FOUND = "not_found"
    FOUND = "found"


T = TypeVar("T")


@dataclass
class ParquetResult(Generic[T]):
    """Generic result wrapper for parquet read/lookup operations.

    Callers check ``result.status == CoverageStatus.FOUND`` before
    accessing ``result.data``.

    Attributes:
        status: One of LOAD_ERROR, NOT_FOUND, or FOUND.
        data: The returned data (present only when status is FOUND).
        error: Human-readable error message (present on LOAD_ERROR or NOT_FOUND).
    """

    status: CoverageStatus
    data: Optional[T] = None
    error: Optional[str] = None
