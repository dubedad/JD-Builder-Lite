"""Statement enrichment service combining CSV lookups with parsed data."""

import logging
from typing import List, Dict, Optional, Tuple, Any
from src.models.noc import EnrichedNOCStatement, ProficiencyLevel, EnrichmentSource
from src.services.csv_loader import guide_csv

logger = logging.getLogger(__name__)

# Work Context classification patterns (from CONTEXT.md)
CLASSIFICATION_PATTERNS = {
    "responsibilities": ["responsib", "decision"],
    "effort": ["effort"]
}


class EnrichmentService:
    """Service for enriching parsed statements with CSV data and classification."""

    def enrich_statement(
        self,
        item: Dict[str, Any],
        category: str,
        source_url: str
    ) -> EnrichedNOCStatement:
        """Enrich a single statement with description and proficiency.

        Args:
            item: dict with {text, level, max, element_id} from parser
            category: "skills", "abilities", "knowledge", "work_activities"
            source_url: OASIS profile URL

        Returns:
            EnrichedNOCStatement with description and proficiency
        """
        text = item.get("text", "")
        level = item.get("level")
        max_level = item.get("max")
        element_id = item.get("element_id")

        # Lookup description from guide_csv
        row = guide_csv.lookup(element_id=element_id, title=text)
        description = row.get("description", "").strip() if row else None
        if description == "":
            description = None

        # Get category definition
        category_definition = guide_csv.get_category_definition(category)

        # Get proficiency level with scale meaning
        proficiency = None
        if level is not None and max_level is not None:
            scale_data = guide_csv.get_scale_meaning(category, level)
            if scale_data:
                proficiency = ProficiencyLevel(
                    level=scale_data["level"],
                    max=scale_data["max"],
                    label=scale_data["label"],
                    dimension=scale_data["dimension"]
                )

        # Create enriched statement
        return EnrichedNOCStatement(
            text=text,
            source_attribute=category.title(),
            source_url=source_url,
            element_id=element_id,
            description=description,
            proficiency=proficiency,
            category_definition=category_definition,
            enrichment_source=EnrichmentSource.GUIDE_CSV,
            confidence=1.0
        )

    def enrich_work_context_statement(
        self,
        item: Dict[str, Any],
        source_url: str
    ) -> EnrichedNOCStatement:
        """Enrich a Work Context statement with classification.

        Args:
            item: dict with {text, level, max, dimension_type}
            source_url: OASIS profile URL

        Returns:
            EnrichedNOCStatement with classification and dimension_type
        """
        text = item.get("text", "")
        level = item.get("level")
        max_level = item.get("max")
        dimension_type = item.get("dimension_type", "Unknown")

        # Lookup description from guide_csv
        row = guide_csv.lookup(title=text)
        description = row.get("description", "").strip() if row else None
        if description == "":
            description = None

        # Classify Work Context item
        classification, reason = self.classify_work_context(text, description)

        # Get category definition for Work Context
        category_definition = guide_csv.get_category_definition("work_context")

        # Get proficiency level - Work Context uses dimension-specific scales
        proficiency = None
        if level is not None and max_level is not None:
            # Map dimension_type to scale key
            dimension_lower = dimension_type.lower()
            scale_key = None

            if "frequency" in dimension_lower or "often" in dimension_lower:
                scale_key = "work_context_frequency"
            elif "duration" in dimension_lower or "time" in dimension_lower:
                scale_key = "work_context_duration"

            if scale_key:
                scale_data = guide_csv.get_scale_meaning(scale_key, level)
                if scale_data:
                    proficiency = ProficiencyLevel(
                        level=scale_data["level"],
                        max=scale_data["max"],
                        label=scale_data["label"],
                        dimension=scale_data["dimension"]
                    )

            # Fallback: use generic level display if no scale match
            if not proficiency:
                proficiency = ProficiencyLevel(
                    level=level,
                    max=max_level,
                    label=f"{level} of {max_level}",
                    dimension=dimension_type
                )

        return EnrichedNOCStatement(
            text=text,
            source_attribute="Work Context",
            source_url=source_url,
            description=description,
            proficiency=proficiency,
            category_definition=category_definition,
            dimension_type=dimension_type,
            classification=classification,
            classification_reason=reason,
            enrichment_source=EnrichmentSource.GUIDE_CSV,
            confidence=1.0
        )

    def classify_work_context(
        self,
        text: str,
        description: Optional[str] = None
    ) -> Tuple[str, str]:
        """Classify Work Context item into responsibilities/effort/other.

        Args:
            text: Item text
            description: Optional description from guide_csv

        Returns:
            Tuple of (classification, reason)
            classification: "responsibilities", "effort", "other_work_context"
            reason: Explanation of classification
        """
        text_lower = text.lower()
        desc_lower = description.lower() if description else ""

        # Check for responsibilities patterns
        responsibilities_match = None
        for pattern in CLASSIFICATION_PATTERNS["responsibilities"]:
            if pattern in text_lower:
                responsibilities_match = f"matched '{pattern}' in text"
                break
            if desc_lower and pattern in desc_lower:
                responsibilities_match = f"matched '{pattern}' in description"
                break

        # Check for effort patterns
        effort_match = None
        for pattern in CLASSIFICATION_PATTERNS["effort"]:
            if pattern in text_lower:
                effort_match = f"matched '{pattern}' in text"
                break
            if desc_lower and pattern in desc_lower:
                effort_match = f"matched '{pattern}' in description"
                break

        # Conflict resolution: responsibilities wins if both match
        if responsibilities_match and effort_match:
            return ("responsibilities", f"{responsibilities_match} (takes precedence over effort)")

        if responsibilities_match:
            return ("responsibilities", responsibilities_match)

        if effort_match:
            return ("effort", effort_match)

        # Default to other_work_context
        return ("other_work_context", "no pattern match")

    def enrich_statements(
        self,
        items: List[Dict[str, Any]],
        category: str,
        source_url: str
    ) -> List[EnrichedNOCStatement]:
        """Enrich and filter a list of statements.

        Args:
            items: List of dicts from parser
            category: Category name
            source_url: OASIS profile URL

        Returns:
            List of enriched statements, filtered (level != 0) and sorted by proficiency
        """
        # Filter out level 0 items
        filtered_items = [
            item for item in items
            if item.get("level") is not None and item.get("level") != 0
        ]

        # Enrich each item
        enriched = [
            self.enrich_statement(item, category, source_url)
            for item in filtered_items
        ]

        # Sort by proficiency level (highest first), then alphabetically by text
        enriched.sort(
            key=lambda s: (
                -(s.proficiency.level if s.proficiency else -1),  # Negative for descending
                s.text.lower()
            )
        )

        return enriched

    def enrich_work_context(
        self,
        items: List[Dict[str, Any]],
        source_url: str
    ) -> Dict[str, List[EnrichedNOCStatement]]:
        """Enrich and classify Work Context items.

        Args:
            items: List of dicts from parser with {text, level, max, dimension_type}
            source_url: OASIS profile URL

        Returns:
            Dict with three keys: responsibilities, effort, other_work_context
            Each value is a List[EnrichedNOCStatement] sorted by level (highest first)
        """
        # Filter out level 0 items
        filtered_items = [
            item for item in items
            if item.get("level") is not None and item.get("level") != 0
        ]

        # Enrich and classify each item
        enriched = [
            self.enrich_work_context_statement(item, source_url)
            for item in filtered_items
        ]

        # Group by classification
        result = {
            "responsibilities": [],
            "effort": [],
            "other_work_context": []
        }

        for stmt in enriched:
            classification = stmt.classification or "other_work_context"
            if classification in result:
                result[classification].append(stmt)

        # Sort each group by proficiency level (highest first), then alphabetically
        for key in result:
            result[key].sort(
                key=lambda s: (
                    -(s.proficiency.level if s.proficiency else -1),
                    s.text.lower()
                )
            )

        return result


# Module-level singleton
enrichment_service = EnrichmentService()
