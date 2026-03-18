"""Evidence extraction and provenance linking for classification decisions.

Provides text span extraction from JD content and TBS source provenance
for full audit trail of classification recommendations.

Per CONTEXT.md: Evidence linking enables transparency and provenance tracking
required for classification compliance.
"""

# Lazy imports - only load when needed
__all__ = ["extractor", "provenance"]
