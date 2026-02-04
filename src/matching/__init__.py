"""Matching engine for occupational group allocation.

Provides structured LLM output models and semantic matching components
for classifying job descriptions to TBS occupational groups.
"""

# Lazy import to avoid circular dependencies
def __getattr__(name):
    if name == "AllocationResult":
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
    "AllocationResult",
    "GroupRecommendation",
    "ReasoningStep",
    "EvidenceSpan",
    "RejectedGroup",
]
