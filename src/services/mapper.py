"""NOC to JD element mapper with provenance tracking."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from src.models.noc import NOCStatement, JDElementData, SourceMetadata, EnrichedNOCStatement, NOCHierarchy, ReferenceAttributes, ProficiencyLevel
from src.models.responses import (
    EnrichedJDElementData, WorkContextData, OtherJobInfo,
    ExclusionItem, HollandInterest, PersonalAttribute, WorkContextItem
)
from src.services.enrichment_service import enrichment_service
from src.services.csv_loader import guide_csv
from src.services.labels_loader import labels_loader
from src.services.profile_parquet_reader import get_all_profile_tabs
from src.config import OASIS_BASE_URL, OASIS_VERSION

# Level labels for parquet-sourced proficiency ratings (index = level - 1).
_LEVEL_LABELS = ["Basic", "Low", "Medium", "High", "Highest"]


def _level_label(level: int) -> str:
    """Return a human-readable label for a proficiency level (1-5)."""
    idx = max(0, min(level - 1, len(_LEVEL_LABELS) - 1))
    return _LEVEL_LABELS[idx]


def _ratings_to_statements(
    ratings: list[dict],
    source_attribute: str,
    source_url: str,
) -> list[EnrichedNOCStatement]:
    """Convert parquet dimension ratings to EnrichedNOCStatement objects.

    Args:
        ratings: List of {'name': str, 'level': int} dicts (sorted by caller).
        source_attribute: e.g. 'Skills', 'Abilities', 'Knowledge', 'Work Activities'.
        source_url: OASIS profile URL for provenance.

    Returns:
        List of EnrichedNOCStatement with ProficiencyLevel set.
    """
    statements = []
    for rating in ratings:
        level = rating["level"]
        statements.append(EnrichedNOCStatement(
            text=rating["name"],
            source_attribute=source_attribute,
            source_url=source_url,
            proficiency=ProficiencyLevel(
                level=level,
                max=5,
                label=f"{level} - {_level_label(level)} Level",
                dimension="Importance",
            ),
        ))
    return statements


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
        code_with_suffix = noc_code if "." in noc_code else f"{noc_code}.00"
        base_url = f"{OASIS_BASE_URL}/OASIS/OASISOccProfile?code={code_with_suffix}&version={OASIS_VERSION}"

        # Fetch parquet data for all 5 tabs upfront (single batch of file reads).
        # Returns dict: tab_key -> (ratings_list, data_source_str)
        parquet_tabs = get_all_profile_tabs(noc_code)

        # Get classified Work Context
        work_context_classified = enrichment_service.enrich_work_context(
            noc_data.get('work_context', []),
            base_url
        )

        # Extract example_titles from reference_attributes (where parser puts it)
        ref_attrs = noc_data.get('reference_attributes')
        example_titles = []
        if ref_attrs:
            # Handle both dict and ReferenceAttributes object
            if hasattr(ref_attrs, 'example_titles'):
                example_titles = ref_attrs.example_titles or []
            elif isinstance(ref_attrs, dict):
                example_titles = ref_attrs.get('example_titles', [])

        # Supplement/fallback: Get example titles from parquet if scraped data is limited
        parquet_titles = labels_loader.get_example_titles(noc_code)
        if parquet_titles:
            # Merge: use parquet as base, add any scraped titles not already present
            scraped_lower = {t.lower() for t in example_titles}
            combined = parquet_titles.copy()
            for t in example_titles:
                if t.lower() not in {p.lower() for p in parquet_titles}:
                    combined.append(t)
            example_titles = combined

        # Get labels from parquet data (NOC 2025 labels from JobForge 2.0)
        profile_labels = labels_loader.get_labels(noc_code)

        return {
            'noc_code': noc_code,
            'title': noc_data['title'],

            # Example titles / "Also known as" (extracted from reference_attributes)
            'example_titles': example_titles,

            # Labels from NOC 2025 parquet data (for NOC Hierarchy level 6)
            'labels': profile_labels,

            # NOC hierarchy (from parser)
            'noc_hierarchy': noc_data.get('noc_hierarchy'),

            # Enriched JD Elements
            'key_activities': self._map_key_activities_enriched(noc_data, base_url, parquet_tabs),
            'skills': self._map_skills_enriched(noc_data, base_url, parquet_tabs),
            'effort': self._map_effort_enriched(noc_code, base_url, parquet_tabs),
            'responsibility': self._map_responsibility_enriched(noc_code, base_url, parquet_tabs),
            'working_conditions': self._map_working_conditions_enriched(noc_data, base_url, parquet_tabs),

            # Classified Work Context (alternative access)
            'work_context': WorkContextData(
                responsibilities=work_context_classified.get('responsibilities', []),
                effort=work_context_classified.get('effort', []),
                other_work_context=work_context_classified.get('other_work_context', [])
            ),

            # Reference attributes (from parser, enriched with parquet lead statement)
            'reference_attributes': self._enrich_reference_attributes(
                noc_data.get('reference_attributes'), noc_code
            ),

            # Other Job Info (for "Other" tab)
            'other_job_info': self._build_other_job_info(noc_code),

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

    def _enrich_reference_attributes(
        self, ref_attrs: Optional[ReferenceAttributes], noc_code: str
    ) -> Optional[ReferenceAttributes]:
        """Inject parquet lead statement into reference_attributes if missing."""
        parquet_lead = labels_loader.get_lead_statement(noc_code)
        if not parquet_lead:
            return ref_attrs
        if ref_attrs is None:
            return ReferenceAttributes(lead_statement=parquet_lead)
        if not ref_attrs.lead_statement:
            return ref_attrs.model_copy(update={'lead_statement': parquet_lead})
        return ref_attrs

    def _map_key_activities_enriched(
        self,
        data: Dict[str, Any],
        url: str,
        parquet_tabs: Optional[dict] = None,
    ) -> EnrichedJDElementData:
        """Map main duties and work activities to enriched Key Activities element.

        Main Duties are ALWAYS sourced from OASIS (element_main_duties.parquet
        has only 8 rows / 3 profiles -- ETL incomplete). Work Activities are
        sourced from parquet when available, otherwise from OASIS enrichment.
        Because Main Duties are always OASIS, this element's data_source is
        always 'oasis'.
        """
        statements = []

        # Main duties: ALWAYS from OASIS (parquet ETL incomplete).
        for duty in data.get('main_duties', []):
            statements.append(EnrichedNOCStatement(
                text=duty,
                source_attribute="Main Duties",
                source_url=url
            ))

        # Work activities: use parquet if available, else fall back to OASIS enrichment.
        wa_ratings, wa_source = (parquet_tabs or {}).get("work_activities", ([], "oasis"))
        if wa_ratings and wa_source == "jobforge":
            statements.extend(_ratings_to_statements(wa_ratings, "Work Activities", url))
        else:
            # OASIS fallback path.
            work_activities = enrichment_service.enrich_statements(
                data.get('work_activities', []),
                'work_activities',
                url
            )
            statements.extend(work_activities)

        # data_source is always "oasis": Main Duties anchor this element to OASIS.
        return EnrichedJDElementData(
            statements=statements,
            category_definition=guide_csv.get_category_definition('key_activities'),
            source_attribute="Key Activities",
            data_source="oasis",
        )

    def _map_skills_enriched(
        self,
        data: Dict[str, Any],
        url: str,
        parquet_tabs: Optional[dict] = None,
    ) -> EnrichedJDElementData:
        """Map skills, abilities, and knowledge to enriched Skills element.

        When parquet data is available for all three sub-dimensions (skills,
        abilities, knowledge), uses parquet ratings and sets data_source='jobforge'.
        Falls back to OASIS enrichment for any dimension where parquet is missing.
        If ALL three come from parquet, data_source='jobforge'; otherwise 'oasis'.
        """
        statements = []
        tabs = parquet_tabs or {}

        skills_ratings, skills_source = tabs.get("skills", ([], "oasis"))
        abilities_ratings, abilities_source = tabs.get("abilities", ([], "oasis"))
        knowledge_ratings, knowledge_source = tabs.get("knowledge", ([], "oasis"))

        all_from_parquet = (
            skills_source == "jobforge"
            and abilities_source == "jobforge"
            and knowledge_source == "jobforge"
        )

        if all_from_parquet:
            # Build combined Skills + Abilities + Knowledge from separate parquet lookups.
            statements.extend(_ratings_to_statements(skills_ratings, "Skills", url))
            statements.extend(_ratings_to_statements(abilities_ratings, "Abilities", url))
            statements.extend(_ratings_to_statements(knowledge_ratings, "Knowledge", url))
            data_source = "jobforge"
        else:
            # OASIS fallback path for all three (keep atomic: all or nothing).
            statements.extend(enrichment_service.enrich_statements(
                data.get('skills', []),
                'skills',
                url
            ))
            statements.extend(enrichment_service.enrich_statements(
                data.get('abilities', []),
                'abilities',
                url
            ))
            statements.extend(enrichment_service.enrich_statements(
                data.get('knowledge', []),
                'knowledge',
                url
            ))
            data_source = "oasis"

        # Sort all by proficiency (highest first).
        statements.sort(
            key=lambda s: (s.proficiency.level if s.proficiency else 0),
            reverse=True
        )

        return EnrichedJDElementData(
            statements=statements,
            category_definition=guide_csv.get_category_definition('skills'),
            source_attribute="Skills",
            data_source=data_source,
        )

    def _map_effort_enriched(self, noc_code: str, url: str, parquet_tabs: Optional[dict] = None) -> EnrichedJDElementData:
        """Map Work Context items to Effort - ALL items NOT in Responsibility."""
        # get_work_context_filtered uses oasis_code format (e.g. '12100.00'), not bare noc_code
        oasis_code = noc_code if '.' in noc_code else f"{noc_code}.00"
        effort_items = labels_loader.get_work_context_filtered(oasis_code, 'effort')

        # data_source: "jobforge" if work_context parquet lookup succeeded, else "oasis"
        _, wc_source = (parquet_tabs or {}).get("work_context", ([], "oasis"))
        data_source = wc_source

        statements = []
        for item in effort_items:
            statements.append(EnrichedNOCStatement(
                text=item['name'],
                source_attribute="Work Context",
                source_url=url,
                description=item.get('description', ''),
                proficiency={
                    'level': item['level'],
                    'max': 5,
                    'label': f"{item['level']} - {'Highest' if item['level'] == 5 else 'High' if item['level'] >= 4 else 'Medium' if item['level'] >= 3 else 'Low' if item['level'] >= 2 else 'Basic'} Level",
                    'dimension': 'Importance'
                } if item['level'] > 0 else None
            ))

        return EnrichedJDElementData(
            statements=statements,
            category_definition=guide_csv.get_category_definition('effort'),
            source_attribute="Work Context - Effort",
            data_source=data_source,
        )

    def _map_responsibility_enriched(self, noc_code: str, url: str, parquet_tabs: Optional[dict] = None) -> EnrichedJDElementData:
        """Map Work Context items containing 'decision' or 'responsib' to Responsibility."""
        # get_work_context_filtered uses oasis_code format (e.g. '12100.00'), not bare noc_code
        oasis_code = noc_code if '.' in noc_code else f"{noc_code}.00"
        resp_items = labels_loader.get_work_context_filtered(oasis_code, 'responsibility')

        # data_source: "jobforge" if work_context parquet lookup succeeded, else "oasis"
        _, wc_source = (parquet_tabs or {}).get("work_context", ([], "oasis"))
        data_source = wc_source

        statements = []
        for item in resp_items:
            statements.append(EnrichedNOCStatement(
                text=item['name'],
                source_attribute="Work Context",
                source_url=url,
                description=item.get('description', ''),
                proficiency={
                    'level': item['level'],
                    'max': 5,
                    'label': f"{item['level']} - {'Highest' if item['level'] == 5 else 'High' if item['level'] >= 4 else 'Medium' if item['level'] >= 3 else 'Low' if item['level'] >= 2 else 'Basic'} Level",
                    'dimension': 'Importance'
                } if item['level'] > 0 else None
            ))

        return EnrichedJDElementData(
            statements=statements,
            category_definition=guide_csv.get_category_definition('responsibility'),
            source_attribute="Work Context - Responsibility",
            data_source=data_source,
        )

    def _map_working_conditions_enriched(self, data: Dict[str, Any], url: str, parquet_tabs: Optional[dict] = None) -> EnrichedJDElementData:
        """Map all Work Context items to Working Conditions."""
        # data_source: "jobforge" if work_context parquet lookup succeeded, else "oasis"
        _, wc_source = (parquet_tabs or {}).get("work_context", ([], "oasis"))
        data_source = wc_source

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
            source_attribute="Work Context",
            data_source=data_source,
        )

    def _build_other_job_info(self, noc_code: str) -> OtherJobInfo:
        """Build OtherJobInfo from JobForge 2.0 data sources."""
        # Exclusions
        exclusions_raw = labels_loader.get_exclusions(noc_code)
        exclusions = [ExclusionItem(code=e['code'], title=e['title']) for e in exclusions_raw]

        # Employment requirements
        employment_requirements = labels_loader.get_employment_requirements(noc_code)

        # Workplaces
        workplaces = labels_loader.get_workplaces(noc_code)

        # Interests (Holland codes)
        interests_raw = labels_loader.get_interests(noc_code)
        interests = [
            HollandInterest(
                code=i['code'],
                title=i['title'],
                description=i['description'],
                rank=i['rank']
            )
            for i in interests_raw
        ]

        # Personal attributes
        attrs_raw = labels_loader.get_personal_attributes(noc_code)
        personal_attributes = [
            PersonalAttribute(name=a['name'], level=a['level'])
            for a in attrs_raw
        ]

        # Work Context from parquet (filtered)
        wc_responsibility = labels_loader.get_work_context_filtered(noc_code, 'responsibility')
        wc_effort = labels_loader.get_work_context_filtered(noc_code, 'effort')

        return OtherJobInfo(
            exclusions=exclusions,
            employment_requirements=employment_requirements,
            workplaces=workplaces,
            interests=interests,
            personal_attributes=personal_attributes,
            work_context_responsibility=[
                WorkContextItem(name=w['name'], level=w['level'])
                for w in wc_responsibility
            ],
            work_context_effort=[
                WorkContextItem(name=w['name'], level=w['level'])
                for w in wc_effort
            ]
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
