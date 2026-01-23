"""NOC to JD element mapper with provenance tracking."""

from typing import Dict, Any, List
from datetime import datetime
from src.models.noc import NOCStatement, JDElementData, SourceMetadata, EnrichedNOCStatement, NOCHierarchy, ReferenceAttributes
from src.models.responses import EnrichedJDElementData, WorkContextData
from src.services.enrichment_service import enrichment_service
from src.services.csv_loader import guide_csv
from src.config import OASIS_BASE_URL, OASIS_VERSION


class JDMapper:
    """Transform parsed NOC data into JD element structure with full provenance."""

    # Keywords for filtering work_context into Effort/Responsibility
    EFFORT_KEYWORDS = ["effort", "physical", "mental", "demand", "strain", "lifting", "standing"]
    RESPONSIBILITY_KEYWORDS = ["responsib", "decision", "supervis", "direct", "manage", "lead", "accountab"]

    def to_jd_elements(self, noc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform NOC data into enriched JD element structure.

        Args:
            noc_data: Dict with noc_code, title, and all profile sections
                      (now includes items as dicts with level/max from parser)

        Returns:
            Dict matching ProfileResponse structure with enriched JD elements
        """
        noc_code = noc_data['noc_code']
        base_url = f"{OASIS_BASE_URL}/OaSIS/OaSISOccProfile?code={noc_code}&version={OASIS_VERSION}"

        # Get classified Work Context
        work_context_classified = enrichment_service.enrich_work_context(
            noc_data.get('work_context', []),
            base_url
        )

        return {
            'noc_code': noc_code,
            'title': noc_data['title'],

            # NOC hierarchy (from parser)
            'noc_hierarchy': noc_data.get('noc_hierarchy'),

            # Enriched JD Elements
            'key_activities': self._map_key_activities_enriched(noc_data, base_url),
            'skills': self._map_skills_enriched(noc_data, base_url),
            'effort': self._map_effort_enriched(work_context_classified, base_url),
            'responsibility': self._map_responsibility_enriched(work_context_classified, base_url),
            'working_conditions': self._map_working_conditions_enriched(noc_data, base_url),

            # Classified Work Context (alternative access)
            'work_context': WorkContextData(
                responsibilities=work_context_classified.get('responsibilities', []),
                effort=work_context_classified.get('effort', []),
                other_work_context=work_context_classified.get('other_work_context', [])
            ),

            # Reference attributes (from parser)
            'reference_attributes': noc_data.get('reference_attributes'),

            'metadata': SourceMetadata(
                noc_code=noc_code,
                profile_url=base_url,
                scraped_at=datetime.utcnow(),
                version=OASIS_VERSION
            ),

            # Enrichment metadata
            'csv_loaded_at': guide_csv.get_loaded_at(),
            'enrichment_stats': guide_csv.get_stats()
        }

    def _map_key_activities_enriched(self, data: Dict[str, Any], url: str) -> EnrichedJDElementData:
        """Map main duties and work activities to enriched Key Activities element."""
        statements = []

        # Main duties (strings, no proficiency)
        for duty in data.get('main_duties', []):
            statements.append(EnrichedNOCStatement(
                text=duty,
                source_attribute="Main Duties",
                source_url=url
            ))

        # Work activities (enriched with proficiency)
        work_activities = enrichment_service.enrich_statements(
            data.get('work_activities', []),
            'work_activities',
            url
        )
        statements.extend(work_activities)

        return EnrichedJDElementData(
            statements=statements,
            category_definition=guide_csv.get_category_definition('key_activities'),
            source_attribute="Key Activities"
        )

    def _map_skills_enriched(self, data: Dict[str, Any], url: str) -> EnrichedJDElementData:
        """Map skills, abilities, and knowledge to enriched Skills element."""
        statements = []

        # Skills
        statements.extend(enrichment_service.enrich_statements(
            data.get('skills', []),
            'skills',
            url
        ))

        # Abilities
        statements.extend(enrichment_service.enrich_statements(
            data.get('abilities', []),
            'abilities',
            url
        ))

        # Knowledge
        statements.extend(enrichment_service.enrich_statements(
            data.get('knowledge', []),
            'knowledge',
            url
        ))

        # Sort all by proficiency (highest first)
        statements.sort(
            key=lambda s: (s.proficiency.level if s.proficiency else 0),
            reverse=True
        )

        return EnrichedJDElementData(
            statements=statements,
            category_definition=guide_csv.get_category_definition('skills'),
            source_attribute="Skills"
        )

    def _map_effort_enriched(self, classified: dict, url: str) -> EnrichedJDElementData:
        """Map classified effort Work Context items."""
        return EnrichedJDElementData(
            statements=classified.get('effort', []),
            category_definition=guide_csv.get_category_definition('effort'),
            source_attribute="Work Context - Effort"
        )

    def _map_responsibility_enriched(self, classified: dict, url: str) -> EnrichedJDElementData:
        """Map classified responsibility Work Context items."""
        return EnrichedJDElementData(
            statements=classified.get('responsibilities', []),
            category_definition=guide_csv.get_category_definition('responsibility'),
            source_attribute="Work Context - Responsibility"
        )

    def _map_working_conditions_enriched(self, data: Dict[str, Any], url: str) -> EnrichedJDElementData:
        """Map all Work Context items to Working Conditions."""
        # Get all work context items enriched
        all_items = enrichment_service.enrich_work_context(
            data.get('work_context', []),
            url
        )

        # Flatten all classified items
        statements = (
            all_items.get('responsibilities', []) +
            all_items.get('effort', []) +
            all_items.get('other_work_context', [])
        )

        return EnrichedJDElementData(
            statements=statements,
            category_definition=guide_csv.get_category_definition('working_conditions'),
            source_attribute="Work Context"
        )

    # DEPRECATED: Old non-enriched methods kept for backward compatibility
    def _map_key_activities(self, data: Dict[str, Any], url: str) -> JDElementData:
        """Map main duties and work activities to Key Activities element.

        Args:
            data: NOC data dict
            url: Profile URL for provenance

        Returns:
            JDElementData with combined duties and activities
        """
        statements = []

        # Main duties
        statements.extend(self._make_statements(
            data.get('main_duties', []),
            "Main Duties",
            url
        ))

        # Work activities
        statements.extend(self._make_statements(
            data.get('work_activities', []),
            "Work Activities",
            url
        ))

        return JDElementData(statements=statements)

    def _map_skills(self, data: Dict[str, Any], url: str) -> JDElementData:
        """Map skills, abilities, and knowledge to Skills element.

        Args:
            data: NOC data dict
            url: Profile URL for provenance

        Returns:
            JDElementData with combined skills, abilities, and knowledge
        """
        statements = []

        # Skills
        statements.extend(self._make_statements(
            data.get('skills', []),
            "Skills",
            url
        ))

        # Abilities
        statements.extend(self._make_statements(
            data.get('abilities', []),
            "Abilities",
            url
        ))

        # Knowledge
        statements.extend(self._make_statements(
            data.get('knowledge', []),
            "Knowledge",
            url
        ))

        return JDElementData(statements=statements)

    def _map_effort(self, data: Dict[str, Any], url: str) -> JDElementData:
        """Map work context items related to effort to Effort element.

        Args:
            data: NOC data dict
            url: Profile URL for provenance

        Returns:
            JDElementData with effort-related context items
        """
        work_context = data.get('work_context', [])

        # Filter for effort-related items
        effort_items = [
            item for item in work_context
            if any(keyword in item.lower() for keyword in self.EFFORT_KEYWORDS)
        ]

        statements = self._make_statements(effort_items, "Work Context - Effort", url)
        return JDElementData(statements=statements)

    def _map_responsibility(self, data: Dict[str, Any], url: str) -> JDElementData:
        """Map work context items related to responsibility to Responsibility element.

        Args:
            data: NOC data dict
            url: Profile URL for provenance

        Returns:
            JDElementData with responsibility-related context items
        """
        work_context = data.get('work_context', [])

        # Filter for responsibility-related items
        responsibility_items = [
            item for item in work_context
            if any(keyword in item.lower() for keyword in self.RESPONSIBILITY_KEYWORDS)
        ]

        statements = self._make_statements(responsibility_items, "Work Context - Responsibility", url)
        return JDElementData(statements=statements)

    def _map_working_conditions(self, data: Dict[str, Any], url: str) -> JDElementData:
        """Map all work context items to Working Conditions element.

        Args:
            data: NOC data dict
            url: Profile URL for provenance

        Returns:
            JDElementData with all work context items
        """
        statements = self._make_statements(
            data.get('work_context', []),
            "Work Context",
            url
        )
        return JDElementData(statements=statements)

    def _make_statements(self, items: List[str], source_attr: str, url: str) -> List[NOCStatement]:
        """Create NOCStatement objects from list of items.

        Args:
            items: List of text items
            source_attr: Source attribute label (e.g., "Main Duties")
            url: Profile URL for provenance

        Returns:
            List of NOCStatement objects with full provenance
        """
        return [
            NOCStatement(
                text=item,
                source_attribute=source_attr,
                source_url=url
            )
            for item in items
        ]


# Module-level singleton for easy import
mapper = JDMapper()
