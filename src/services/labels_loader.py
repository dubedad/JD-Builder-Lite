"""Labels, Example Titles, and Other Job Info loader from JobForge 2.0 data."""

import logging
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Check if pandas and pyarrow are available for parquet support
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


# Holland code definitions (RIASEC model)
HOLLAND_CODES = {
    'R': {
        'title': 'Realistic',
        'description': 'Practical, hands-on activities and jobs that involve working with tools, machines, or animals.'
    },
    'I': {
        'title': 'Investigative',
        'description': 'Thinking, analyzing, and problem-solving activities that involve research and scientific exploration.'
    },
    'A': {
        'title': 'Artistic',
        'description': 'Creative activities that involve art, design, language, and self-expression.'
    },
    'S': {
        'title': 'Social',
        'description': 'Helping, teaching, counseling, or providing service to others.'
    },
    'E': {
        'title': 'Enterprising',
        'description': 'Leading, persuading, and managing others to achieve organizational or economic goals.'
    },
    'C': {
        'title': 'Conventional',
        'description': 'Organizing, managing data, and following procedures in structured environments.'
    }
}


# Work Context element descriptions (from OASIS guide)
WORK_CONTEXT_DESCRIPTIONS = {
    'Freedom to Make Decisions': 'The job allows the worker to make decisions without supervision.',
    'Frequency of Decision Making': 'The job requires the worker to make decisions that affect other people, the financial resources, and/or the image and reputation of the organization.',
    'Impact of Decisions': 'The impact on the organization or colleagues of the decisions made by the worker (a decision should be understood as a conclusion or resolution reached after consideration).',
    'Responsibility for Outcomes and Results of Other Workers': 'The job requires assuming the responsibility for the end product and effects of other workers\' work.',
    "Responsible for Others' Health and Safety": 'The job requires ensuring the health, safety and security of others.',
    'Automation': 'The level of automation involved in the job.',
    'Competition': 'The level of competition in this job.',
    'Consequence of Error': 'The seriousness of consequences resulting from errors in this job.',
    'Pace Determined by Speed of Equipment': 'The pace of work is determined by the speed of equipment or machinery.',
    'Precision': 'The level of precision required in performing this job.',
    'Structured versus Unstructured Work': 'The extent to which the job is structured or unstructured.',
    'Tasks Repetition': 'The frequency of repeating the same physical activities or mental processes.',
    'Time Pressure': 'The level of time pressure involved in the job.',
    'Work Schedule': 'The regularity of the work schedule.',
    'Work Week Duration': 'The typical duration of a work week.',
    'Biological Agents': 'Exposure to biological agents in the workplace.',
    'Dangerous Chemical Substances': 'Exposure to dangerous chemical substances.',
    'Extremely Bright or Inadequate Lighting': 'Working in extremely bright or inadequate lighting conditions.',
    'Extreme Temperatures': 'Working in extreme temperature conditions.',
    'Hazardous Conditions': 'Exposure to hazardous conditions.',
    'Hazardous Equipment, Machinery, Tools': 'Working with hazardous equipment, machinery, or tools.',
    'High Places': 'Working in high places.',
    'Physical Proximity': 'The physical proximity to other people required by this job.',
    'Sound and Noise': 'Exposure to sounds and noise levels.',
    'Vibration': 'Exposure to vibration.',
    'Skin Injury': 'Risk of skin injury.',
    'Bending or Twisting the Body': 'Physical activity requiring bending or twisting the body.',
    'Climbing': 'Physical activity requiring climbing.',
    'Cramped Work Space, Awkward Positions': 'Working in cramped work spaces or awkward positions.',
    'Handling Material Manually': 'Handling materials manually.',
    'Keeping or Regaining Balance': 'Keeping or regaining balance.',
    'Making Repetitive Motions': 'Making repetitive motions.',
    'Sitting': 'Amount of time spent sitting.',
    'Standing': 'Amount of time spent standing.',
    'Walking and Running': 'Amount of time spent walking or running.',
    'Conflict Situations': 'Frequency of conflict situations.',
    'Contact With Others': 'The amount of contact with others required by this job.',
    'Coordinating or Leading Others': 'Coordinating or leading others.',
    'Deal With External Customers': 'Dealing with external customers.',
    'Deal With Physically Aggressive People': 'Dealing with physically aggressive people.',
    'Dealing With Unpleasant or Angry People': 'Dealing with unpleasant or angry people.',
    'Electronic Mail': 'Use of electronic mail.',
    'Face-to-Face Discussions': 'Frequency of face-to-face discussions.',
    'Written Communications': 'Use of written communications.',
    'Public Speaking': 'Frequency of public speaking.',
    'Telephone': 'Use of telephone.',
    'Work With Work Group or Team': 'Working with a work group or team.',
}


class LabelsLoader:
    """Load and retrieve NOC labels, example titles, and other job info from parquet/CSV files."""

    # Path to JobForge 2.0 data (external dependency)
    GOLD_DATA_PATH = Path(os.getenv(
        "JOBFORGE_GOLD_PATH",
        "/Users/victornishi/Documents/GitHub/JobForge-2.0/data/gold"
    ))
    SOURCE_DATA_PATH = Path(os.getenv(
        "JOBFORGE_SOURCE_PATH",
        "/Users/victornishi/Documents/GitHub/JobForge-2.0/data/source"
    ))

    # Parquet files (gold)
    LABELS_FILE = GOLD_DATA_PATH / "element_labels.parquet"
    EXAMPLE_TITLES_FILE = GOLD_DATA_PATH / "element_example_titles.parquet"
    EXCLUSIONS_FILE = GOLD_DATA_PATH / "element_exclusions.parquet"
    EMPLOYMENT_REQS_FILE = GOLD_DATA_PATH / "element_employment_requirements.parquet"
    WORKPLACES_FILE = GOLD_DATA_PATH / "element_workplaces_employers.parquet"
    WORK_CONTEXT_FILE = GOLD_DATA_PATH / "oasis_workcontext.parquet"

    # CSV files (source)
    INTERESTS_FILE = SOURCE_DATA_PATH / "interests_oasis_2023_v1.0.csv"
    PERSONAL_ATTRS_FILE = SOURCE_DATA_PATH / "personal-attributes_oasis_2023_v1.0.csv"

    def __init__(self):
        self._labels_df = None
        self._titles_df = None
        self._exclusions_df = None
        self._employment_reqs_df = None
        self._workplaces_df = None
        self._interests_df = None
        self._personal_attrs_df = None
        self._work_context_df = None

        # Caches
        self._labels_cache = {}
        self._titles_cache = {}
        self._exclusions_cache = {}
        self._employment_reqs_cache = {}
        self._workplaces_cache = {}
        self._interests_cache = {}
        self._personal_attrs_cache = {}
        self._work_context_cache = {}

        self._load_error = None

    def _load_labels(self) -> bool:
        """Load the labels parquet file if not already loaded."""
        if self._labels_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Labels load skipped: pandas/pyarrow not installed")
            self._load_error = "pandas/pyarrow not installed for parquet support"
            return False

        if not self.LABELS_FILE.exists():
            logger.warning("Labels file not found: %s", self.LABELS_FILE)
            self._load_error = f"Labels file not found: {self.LABELS_FILE}"
            return False

        try:
            self._labels_df = pd.read_parquet(self.LABELS_FILE)
            logger.info("LabelsLoader: loaded %d labels from parquet", len(self._labels_df))
            return True
        except Exception as e:
            logger.warning("Failed to load labels from %s: %s", self.LABELS_FILE, e)
            self._load_error = f"Failed to load labels: {e}"
            return False

    def _load_example_titles(self) -> bool:
        """Load the example titles parquet file if not already loaded."""
        if self._titles_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Example titles load skipped: pandas/pyarrow not installed")
            self._load_error = "pandas/pyarrow not installed for parquet support"
            return False

        if not self.EXAMPLE_TITLES_FILE.exists():
            logger.warning("Example titles file not found: %s", self.EXAMPLE_TITLES_FILE)
            self._load_error = f"Example titles file not found: {self.EXAMPLE_TITLES_FILE}"
            return False

        try:
            self._titles_df = pd.read_parquet(self.EXAMPLE_TITLES_FILE)
            logger.info("LabelsLoader: loaded %d example titles from parquet", len(self._titles_df))
            return True
        except Exception as e:
            logger.warning("Failed to load example titles from %s: %s", self.EXAMPLE_TITLES_FILE, e)
            self._load_error = f"Failed to load example titles: {e}"
            return False

    def get_labels(self, oasis_profile_code: str) -> List[str]:
        """Get all labels for a given OaSIS profile code.

        Args:
            oasis_profile_code: OaSIS code like '21211.00'

        Returns:
            List of label strings for the profile
        """
        # Check cache first
        if oasis_profile_code in self._labels_cache:
            return self._labels_cache[oasis_profile_code]

        # Try to load data
        if not self._load_labels():
            return []

        # Query labels for this profile
        try:
            matching = self._labels_df[
                self._labels_df['oasis_profile_code'] == oasis_profile_code
            ]['Label'].tolist()

            # Cache and return
            self._labels_cache[oasis_profile_code] = matching
            return matching
        except Exception as e:
            logger.warning("LabelsLoader: error querying labels: %s", e)
            return []

    def get_example_titles(self, oasis_profile_code: str) -> List[str]:
        """Get all example job titles for a given OaSIS profile code.

        Args:
            oasis_profile_code: OaSIS code like '21211.00'

        Returns:
            List of example title strings for the profile
        """
        # Check cache first
        if oasis_profile_code in self._titles_cache:
            return self._titles_cache[oasis_profile_code]

        # Try to load data
        if not self._load_example_titles():
            return []

        # Query example titles for this profile
        try:
            matching = self._titles_df[
                self._titles_df['oasis_profile_code'] == oasis_profile_code
            ]['Job title text'].tolist()

            # Cache and return
            self._titles_cache[oasis_profile_code] = matching
            return matching
        except Exception as e:
            logger.warning("LabelsLoader: error querying example titles: %s", e)
            return []

    def _load_exclusions(self) -> bool:
        """Load the exclusions parquet file if not already loaded."""
        if self._exclusions_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Exclusions load skipped: pandas/pyarrow not installed")
            return False

        if not self.EXCLUSIONS_FILE.exists():
            logger.warning("Exclusions file not found: %s", self.EXCLUSIONS_FILE)
            return False

        try:
            self._exclusions_df = pd.read_parquet(self.EXCLUSIONS_FILE)
            return True
        except Exception as e:
            logger.warning("Failed to load exclusions from %s: %s", self.EXCLUSIONS_FILE, e)
            return False

    def _load_employment_reqs(self) -> bool:
        """Load the employment requirements parquet file if not already loaded."""
        if self._employment_reqs_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Employment requirements load skipped: pandas/pyarrow not installed")
            return False

        if not self.EMPLOYMENT_REQS_FILE.exists():
            logger.warning("Employment requirements file not found: %s", self.EMPLOYMENT_REQS_FILE)
            return False

        try:
            self._employment_reqs_df = pd.read_parquet(self.EMPLOYMENT_REQS_FILE)
            return True
        except Exception as e:
            logger.warning("Failed to load employment requirements from %s: %s", self.EMPLOYMENT_REQS_FILE, e)
            return False

    def _load_workplaces(self) -> bool:
        """Load the workplaces parquet file if not already loaded."""
        if self._workplaces_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Workplaces load skipped: pandas/pyarrow not installed")
            return False

        if not self.WORKPLACES_FILE.exists():
            logger.warning("Workplaces file not found: %s", self.WORKPLACES_FILE)
            return False

        try:
            self._workplaces_df = pd.read_parquet(self.WORKPLACES_FILE)
            return True
        except Exception as e:
            logger.warning("Failed to load workplaces from %s: %s", self.WORKPLACES_FILE, e)
            return False

    def _load_interests(self) -> bool:
        """Load the interests CSV file if not already loaded."""
        if self._interests_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Interests load skipped: pandas/pyarrow not installed")
            return False

        if not self.INTERESTS_FILE.exists():
            logger.warning("Interests file not found: %s", self.INTERESTS_FILE)
            return False

        try:
            self._interests_df = pd.read_csv(self.INTERESTS_FILE)
            return True
        except Exception as e:
            logger.warning("Failed to load interests from %s: %s", self.INTERESTS_FILE, e)
            return False

    def _load_personal_attrs(self) -> bool:
        """Load the personal attributes CSV file if not already loaded."""
        if self._personal_attrs_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Personal attributes load skipped: pandas/pyarrow not installed")
            return False

        if not self.PERSONAL_ATTRS_FILE.exists():
            logger.warning("Personal attributes file not found: %s", self.PERSONAL_ATTRS_FILE)
            return False

        try:
            self._personal_attrs_df = pd.read_csv(self.PERSONAL_ATTRS_FILE)
            return True
        except Exception as e:
            logger.warning("Failed to load personal attributes from %s: %s", self.PERSONAL_ATTRS_FILE, e)
            return False

    def _load_work_context(self) -> bool:
        """Load the work context parquet file if not already loaded."""
        if self._work_context_df is not None:
            return True

        if not HAS_PANDAS:
            logger.warning("Work context load skipped: pandas/pyarrow not installed")
            return False

        if not self.WORK_CONTEXT_FILE.exists():
            logger.warning("Work context file not found: %s", self.WORK_CONTEXT_FILE)
            return False

        try:
            self._work_context_df = pd.read_parquet(self.WORK_CONTEXT_FILE)
            return True
        except Exception as e:
            logger.warning("Failed to load work context from %s: %s", self.WORK_CONTEXT_FILE, e)
            return False

    def get_exclusions(self, oasis_profile_code: str) -> List[Dict[str, str]]:
        """Get exclusions for a given OaSIS profile code.

        Returns:
            List of dicts with 'code' and 'title' keys
        """
        if oasis_profile_code in self._exclusions_cache:
            return self._exclusions_cache[oasis_profile_code]

        if not self._load_exclusions():
            return []

        try:
            matching = self._exclusions_df[
                self._exclusions_df['oasis_profile_code'] == oasis_profile_code
            ]
            exclusions = [
                {'code': str(row['Excluded code']), 'title': row['Job title']}
                for _, row in matching.iterrows()
                if pd.notna(row['Job title'])
            ]
            self._exclusions_cache[oasis_profile_code] = exclusions
            return exclusions
        except Exception as e:
            logger.warning("LabelsLoader: error querying exclusions for %s: %s", oasis_profile_code, e)
            return []

    def get_employment_requirements(self, oasis_profile_code: str) -> List[str]:
        """Get employment requirements for a given OaSIS profile code."""
        if oasis_profile_code in self._employment_reqs_cache:
            return self._employment_reqs_cache[oasis_profile_code]

        if not self._load_employment_reqs():
            return []

        try:
            matching = self._employment_reqs_df[
                self._employment_reqs_df['oasis_profile_code'] == oasis_profile_code
            ]['Employment requirement'].tolist()
            self._employment_reqs_cache[oasis_profile_code] = matching
            return matching
        except Exception as e:
            logger.warning("LabelsLoader: error querying employment requirements for %s: %s", oasis_profile_code, e)
            return []

    def get_workplaces(self, oasis_profile_code: str) -> List[str]:
        """Get workplaces/employers for a given OaSIS profile code."""
        if oasis_profile_code in self._workplaces_cache:
            return self._workplaces_cache[oasis_profile_code]

        if not self._load_workplaces():
            return []

        try:
            matching = self._workplaces_df[
                self._workplaces_df['oasis_profile_code'] == oasis_profile_code
            ]['Workplace/employer name'].tolist()
            self._workplaces_cache[oasis_profile_code] = matching
            return matching
        except Exception as e:
            logger.warning("LabelsLoader: error querying workplaces for %s: %s", oasis_profile_code, e)
            return []

    def get_interests(self, oasis_profile_code: str) -> List[Dict[str, Any]]:
        """Get Holland code interests for a given OaSIS profile code.

        Returns:
            List of dicts with 'code', 'title', 'description', 'rank' keys
        """
        if oasis_profile_code in self._interests_cache:
            return self._interests_cache[oasis_profile_code]

        if not self._load_interests():
            return []

        try:
            # Convert profile code to float for matching (21232.00 -> 21232.0)
            oasis_code = float(oasis_profile_code)

            matching = self._interests_df[
                self._interests_df['OaSIS Code'] == oasis_code
            ]

            if matching.empty:
                return []

            row = matching.iloc[0]
            interests = []
            for i, col in enumerate(['Holland Codes - 1', 'Holland Codes - 2', 'Holland Codes - 3'], 1):
                code = str(row[col]).strip().upper() if pd.notna(row[col]) else ''
                if code and code in HOLLAND_CODES:
                    interests.append({
                        'code': code,
                        'title': HOLLAND_CODES[code]['title'],
                        'description': HOLLAND_CODES[code]['description'],
                        'rank': i
                    })

            self._interests_cache[oasis_profile_code] = interests
            return interests
        except Exception as e:
            logger.warning("LabelsLoader: error querying interests for %s: %s", oasis_profile_code, e)
            return []

    def get_personal_attributes(self, oasis_profile_code: str) -> List[Dict[str, Any]]:
        """Get personal attributes for a given OaSIS profile code.

        Returns:
            List of dicts with 'name' and 'level' keys, sorted by level descending
        """
        if oasis_profile_code in self._personal_attrs_cache:
            return self._personal_attrs_cache[oasis_profile_code]

        if not self._load_personal_attrs():
            return []

        try:
            # Convert profile code to float for matching (21232.00 -> 21232.0)
            oasis_code = float(oasis_profile_code)

            matching = self._personal_attrs_df[
                self._personal_attrs_df['OaSIS Code - Final'] == oasis_code
            ]

            if matching.empty:
                return []

            row = matching.iloc[0]
            attributes = []

            # Get all attribute columns (skip the first two which are code and label)
            for col in self._personal_attrs_df.columns[2:]:
                # Clean column name (remove non-breaking spaces, leading spaces)
                clean_name = col.strip().replace('\xa0', '').strip()
                if clean_name and pd.notna(row[col]):
                    try:
                        level = int(row[col])
                        attributes.append({
                            'name': clean_name,
                            'level': level
                        })
                    except (ValueError, TypeError):
                        pass

            # Sort by level descending
            attributes.sort(key=lambda x: x['level'], reverse=True)
            self._personal_attrs_cache[oasis_profile_code] = attributes
            return attributes
        except Exception as e:
            logger.warning("LabelsLoader: error querying personal attributes for %s: %s", oasis_profile_code, e)
            return []

    def get_work_context_filtered(self, oasis_profile_code: str, filter_type: str = 'all') -> List[Dict[str, Any]]:
        """Get Work Context data filtered by type.

        Args:
            oasis_profile_code: OaSIS code like '21211.00'
            filter_type: 'responsibility', 'effort', 'decision', or 'all'

        Returns:
            List of dicts with 'name', 'level', and 'description' keys
        """
        cache_key = f"{oasis_profile_code}_{filter_type}"
        if cache_key in self._work_context_cache:
            return self._work_context_cache[cache_key]

        if not self._load_work_context():
            return []

        try:
            matching = self._work_context_df[
                self._work_context_df['oasis_code'] == oasis_profile_code
            ]

            if matching.empty:
                return []

            row = matching.iloc[0]
            results = []

            # Skip metadata columns
            skip_cols = ['unit_group_id', 'noc_element_code', 'oasis_code', 'oasis_label',
                        '_source_file', '_ingested_at', '_batch_id', '_layer']

            # Get all Work Context element columns
            all_wc_cols = [c for c in self._work_context_df.columns if c not in skip_cols]

            # Dynamic filtering by element name:
            # Responsibility: columns containing "decision" OR "responsib" (case-insensitive)
            responsibility_cols = [c for c in all_wc_cols
                                   if 'decision' in c.lower() or 'responsib' in c.lower()]

            # Effort: ALL remaining columns NOT in responsibility
            effort_cols = [c for c in all_wc_cols if c not in responsibility_cols]

            # Determine which columns to use
            if filter_type == 'responsibility':
                target_cols = responsibility_cols
            elif filter_type == 'effort':
                target_cols = effort_cols
            else:
                target_cols = all_wc_cols

            for col in target_cols:
                if col in row.index:
                    val = row[col]
                    if pd.notna(val):
                        try:
                            level = int(val)
                            if level > 0:  # Only include non-zero values
                                results.append({
                                    'name': col.strip(),
                                    'level': level,
                                    'description': WORK_CONTEXT_DESCRIPTIONS.get(col.strip(), '')
                                })
                        except (ValueError, TypeError):
                            pass

            # Sort by level descending
            results.sort(key=lambda x: x['level'], reverse=True)
            self._work_context_cache[cache_key] = results
            return results
        except Exception as e:
            logger.warning("LabelsLoader: error querying work context for %s (filter=%s): %s", oasis_profile_code, filter_type, e)
            return []

    def get_error(self) -> Optional[str]:
        """Get any loading error message."""
        return self._load_error

    def is_available(self) -> bool:
        """Check if labels data is available."""
        return self._load_labels()


# Module-level singleton
labels_loader = LabelsLoader()
