"""OaSIS data provenance mapping for compliance reporting.

Maps source_attribute values to their authoritative OaSIS tables on open.canada.ca
with publication dates and URLs for TBS Directive compliance.
"""

from typing import Dict, Optional
from dataclasses import dataclass


# OaSIS dataset base URL on Open Canada portal
OASIS_DATASET_URL = "https://open.canada.ca/data/en/dataset/10ce43bd-fb58-4969-806b-4bffebc87bec"

# Dataset-level publication date (from portal metadata)
OASIS_DATASET_PUBLICATION_DATE = "2025-10-30"


@dataclass
class OaSISTableMetadata:
    """Metadata for an OaSIS data table."""
    table_name: str  # Display name (e.g., "Skills 2025 v1.0")
    publication_date: str  # ISO date string
    resource_url: str  # Full URL to the resource on open.canada.ca


# Mapping from source_attribute to OaSIS table metadata
# Source attributes come from parser.py and enrichment_service.py
OASIS_SOURCE_MAPPING: Dict[str, OaSISTableMetadata] = {
    # Key Activities sources
    "Main Duties": OaSISTableMetadata(
        table_name="Main Duties 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-6"
    ),
    "Work Activities": OaSISTableMetadata(
        table_name="Work Activities 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-10"
    ),

    # Skills sources
    "Skills": OaSISTableMetadata(
        table_name="Skills 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-2"
    ),
    "Abilities": OaSISTableMetadata(
        table_name="Abilities 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-4"
    ),
    "Knowledge": OaSISTableMetadata(
        table_name="Knowledges 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-8"
    ),

    # Work Context sources (Effort and Responsibility)
    "Work Context": OaSISTableMetadata(
        table_name="Work Context 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-12"
    ),
    "Work Context - Effort": OaSISTableMetadata(
        table_name="Work Context 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-12"
    ),
    "Work Context - Responsibility": OaSISTableMetadata(
        table_name="Work Context 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-12"
    ),

    # Reference attributes
    "Example Titles": OaSISTableMetadata(
        table_name="Example Titles 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-26"
    ),
    "Lead Statement": OaSISTableMetadata(
        table_name="Lead Statement 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-22"
    ),
    "Employment Requirements": OaSISTableMetadata(
        table_name="Employment Requirements 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-28"
    ),
    "Additional Information": OaSISTableMetadata(
        table_name="Additional Information 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-30"
    ),
    "Exclusions": OaSISTableMetadata(
        table_name="Exclusions 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-32"
    ),
    "Interests": OaSISTableMetadata(
        table_name="Interests 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-14"
    ),
    "Personal Attributes": OaSISTableMetadata(
        table_name="Personal Attributes 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-6"
    ),
    "Core Competencies": OaSISTableMetadata(
        table_name="Core Competencies 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-16"
    ),
    "Workplaces": OaSISTableMetadata(
        table_name="Workplaces Employers 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-24"
    ),
    "Labels": OaSISTableMetadata(
        table_name="Labels 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-20"
    ),

    # Guide definitions
    "Guide": OaSISTableMetadata(
        table_name="Guide 2025 v1.0",
        publication_date="2025-10-30",
        resource_url=f"{OASIS_DATASET_URL}#wb-auto-0"
    ),
}


def get_provenance_metadata(source_attribute: str) -> Optional[OaSISTableMetadata]:
    """
    Get OaSIS provenance metadata for a source attribute.

    Args:
        source_attribute: The source attribute name (e.g., "Main Duties", "Skills")

    Returns:
        OaSISTableMetadata if found, None otherwise
    """
    # Direct lookup
    if source_attribute in OASIS_SOURCE_MAPPING:
        return OASIS_SOURCE_MAPPING[source_attribute]

    # Try partial matching for compound attributes
    for key, metadata in OASIS_SOURCE_MAPPING.items():
        if key.lower() in source_attribute.lower():
            return metadata

    # Default fallback - return dataset-level info
    return OaSISTableMetadata(
        table_name="OaSIS 2025 v1.0",
        publication_date=OASIS_DATASET_PUBLICATION_DATE,
        resource_url=OASIS_DATASET_URL
    )


def get_publication_date(source_attribute: str) -> str:
    """Get publication date for a source attribute."""
    metadata = get_provenance_metadata(source_attribute)
    return metadata.publication_date if metadata else OASIS_DATASET_PUBLICATION_DATE


def get_source_table_url(source_attribute: str) -> str:
    """Get OaSIS table URL for a source attribute."""
    metadata = get_provenance_metadata(source_attribute)
    return metadata.resource_url if metadata else OASIS_DATASET_URL
