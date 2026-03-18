"""
Matching Engine for Occupational Group Allocation.

Phase 15: Classification Step 1 - Match job descriptions to TBS occupational
groups using the prescribed allocation method.

Public API:
    OccupationalGroupAllocator - Main allocation engine
    allocate_jd - Convenience function for single allocation
    AllocationResult - Pydantic model for allocation results
    GroupRecommendation - Pydantic model for recommendations
    ReasoningStep - Pydantic model for chain-of-thought steps
    EvidenceSpan - Pydantic model for evidence linking
    RejectedGroup - Pydantic model for rejected alternatives
"""

# Lazy import to avoid circular dependencies and heavy model loading
def __getattr__(name):
    if name == "OccupationalGroupAllocator":
        from .allocator import OccupationalGroupAllocator
        return OccupationalGroupAllocator
    elif name == "allocate_jd":
        from .allocator import allocate_jd
        return allocate_jd
    elif name == "AllocationResult":
        from .models import AllocationResult
        return AllocationResult
    elif name == "GroupRecommendation":
        from .models import GroupRecommendation
        return GroupRecommendation
    elif name == "ReasoningStep":
        from .models import ReasoningStep
        return ReasoningStep
    elif name == "EvidenceSpan":
        from .models import EvidenceSpan
        return EvidenceSpan
    elif name == "RejectedGroup":
        from .models import RejectedGroup
        return RejectedGroup
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "OccupationalGroupAllocator",
    "allocate_jd",
    "AllocationResult",
    "GroupRecommendation",
    "ReasoningStep",
    "EvidenceSpan",
    "RejectedGroup",
]
