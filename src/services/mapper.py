"""NOC to JD element mapper with provenance tracking."""

from typing import Dict, Any, List
from datetime import datetime
from src.models.noc import NOCStatement, JDElementData, SourceMetadata
from src.config import OASIS_BASE_URL, OASIS_VERSION


class JDMapper:
    """Transform parsed NOC data into JD element structure with full provenance."""

    # Keywords for filtering work_context into Effort/Responsibility
    EFFORT_KEYWORDS = ["effort", "physical", "mental", "demand", "strain", "lifting", "standing"]
    RESPONSIBILITY_KEYWORDS = ["responsib", "decision", "supervis", "direct", "manage", "lead", "accountab"]

    def to_jd_elements(self, noc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform NOC data into JD element structure.

        Args:
            noc_data: Dict with noc_code, title, and all profile sections

        Returns:
            Dict matching ProfileResponse structure with JD elements and metadata
        """
        noc_code = noc_data['noc_code']
        base_url = f"{OASIS_BASE_URL}/OaSIS/OaSISOccProfile?code={noc_code}&version={OASIS_VERSION}"

        return {
            'noc_code': noc_code,
            'title': noc_data['title'],
            'key_activities': self._map_key_activities(noc_data, base_url),
            'skills': self._map_skills(noc_data, base_url),
            'effort': self._map_effort(noc_data, base_url),
            'responsibility': self._map_responsibility(noc_data, base_url),
            'working_conditions': self._map_working_conditions(noc_data, base_url),
            'metadata': SourceMetadata(
                noc_code=noc_code,
                profile_url=base_url,
                scraped_at=datetime.utcnow(),
                version=OASIS_VERSION
            )
        }

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
