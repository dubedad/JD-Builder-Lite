"""DAMA-DMBOK 2.0 compliant validation for scraped occupational group data.

Provides validation functions for completeness, consistency, and accuracy
checks, ensuring data quality before database insertion.

Per CONTEXT.md: "Never insert partial or corrupt data"
"""

import re
from typing import Dict, List, Any, Optional, Set


class ValidationError(Exception):
    """Custom exception for validation failures.

    Attributes:
        errors: List of validation error messages
    """

    def __init__(self, errors: List[str]):
        """Initialize with list of errors.

        Args:
            errors: List of validation error messages
        """
        self.errors = errors
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format errors into readable message."""
        if not self.errors:
            return "Validation failed (no specific errors)"
        if len(self.errors) == 1:
            return f"Validation failed: {self.errors[0]}"
        return f"Validation failed with {len(self.errors)} errors:\n" + "\n".join(
            f"  - {e}" for e in self.errors
        )

    def __str__(self) -> str:
        return self._format_message()


def validate_completeness(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Check that all required fields exist and are non-empty.

    Per DAMA-DMBOK 2.0: "Complete data has all required values present."

    Args:
        data: Dictionary to validate
        required_fields: List of field names that must be present and non-empty

    Returns:
        List of error messages (empty if valid)

    Example:
        >>> errors = validate_completeness({'group_code': 'AI'}, ['group_code', 'definition'])
        >>> print(errors)
        ['Missing required field: definition']
    """
    errors = []

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None:
            errors.append(f"Null value for required field: {field}")
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f"Empty value for: {field}")

    return errors


def validate_consistency(groups: List[Dict[str, Any]]) -> List[str]:
    """Check data consistency across a set of groups.

    Per DAMA-DMBOK 2.0: "Consistent data does not conflict with other data."

    Checks:
    - No duplicate group_code + subgroup combinations
    - Inclusions/exclusions have valid structure

    Args:
        groups: List of group dictionaries to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check for duplicate group_code + subgroup combinations
    seen_codes: Set[str] = set()

    for idx, group in enumerate(groups):
        code = group.get("group_code", "")
        subgroup = group.get("subgroup")

        # Create unique key
        key = f"{code}|{subgroup or ''}"

        if key in seen_codes:
            errors.append(
                f"Duplicate group_code+subgroup at index {idx}: {code}"
                + (f"/{subgroup}" if subgroup else "")
            )
        else:
            seen_codes.add(key)

        # Validate inclusions structure
        inclusions = group.get("inclusions", [])
        if inclusions:
            seen_orders: Set[int] = set()
            for i, incl in enumerate(inclusions):
                if not isinstance(incl, dict):
                    errors.append(f"Group {code}: inclusion {i} is not a dict")
                    continue
                order = incl.get("order")
                if order in seen_orders:
                    errors.append(f"Group {code}: duplicate inclusion order {order}")
                elif order is not None:
                    seen_orders.add(order)

        # Validate exclusions structure
        exclusions = group.get("exclusions", [])
        if exclusions:
            seen_orders = set()
            for i, excl in enumerate(exclusions):
                if not isinstance(excl, dict):
                    errors.append(f"Group {code}: exclusion {i} is not a dict")
                    continue
                order = excl.get("order")
                if order in seen_orders:
                    errors.append(f"Group {code}: duplicate exclusion order {order}")
                elif order is not None:
                    seen_orders.add(order)

    return errors


def validate_accuracy(data: Dict[str, Any]) -> List[str]:
    """Check data accuracy (format and value correctness).

    Per DAMA-DMBOK 2.0: "Accurate data correctly represents the real-world entity."

    Checks:
    - group_code format (2-4 uppercase letters)
    - URL format (starts with http:// or https://)
    - Timestamp format (ISO 8601)

    Args:
        data: Dictionary with fields to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate group_code format
    group_code = data.get("group_code")
    if group_code is not None and group_code != "":
        if not re.match(r"^[A-Z]{2,4}$", group_code):
            errors.append(
                f"Invalid group_code format '{group_code}': must be 2-4 uppercase letters"
            )

    # Validate URL fields
    url_fields = [
        "definition_url",
        "qualification_standard_url",
        "rates_of_pay_represented_url",
        "rates_of_pay_unrepresented_url",
        "job_evaluation_standard_url",
    ]

    for field in url_fields:
        url = data.get(field)
        if url is not None and url != "":
            if not url.startswith(("http://", "https://")):
                errors.append(f"Invalid URL format for {field}: must start with http:// or https://")

    # Validate timestamp fields (ISO 8601)
    timestamp_fields = ["scraped_at", "effective_from", "effective_to"]
    iso_pattern = r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"

    for field in timestamp_fields:
        timestamp = data.get(field)
        if timestamp is not None and timestamp != "":
            if not re.match(iso_pattern, timestamp):
                errors.append(
                    f"Invalid timestamp format for {field}: must be ISO 8601 format"
                )

    return errors


def validate_group(group: Dict[str, Any]) -> List[str]:
    """Convenience function combining all validations for a single group.

    Runs completeness, accuracy, and structural validations on a group dict.

    Args:
        group: Group dictionary to validate

    Returns:
        Combined list of all validation errors (empty if valid)
    """
    errors = []

    # Completeness: group_code and definition are required
    errors.extend(validate_completeness(group, ["group_code", "definition"]))

    # Accuracy: format checks
    errors.extend(validate_accuracy(group))

    # Structural checks for inclusions/exclusions
    inclusions = group.get("inclusions", [])
    if not isinstance(inclusions, list):
        errors.append("Inclusions is not a list")
    else:
        for i, incl in enumerate(inclusions):
            if not isinstance(incl, dict):
                errors.append(f"Inclusion {i} is not a dict")
            elif not incl.get("statement"):
                errors.append(f"Inclusion {i} missing statement")
            elif "order" not in incl:
                errors.append(f"Inclusion {i} missing order")

    exclusions = group.get("exclusions", [])
    if not isinstance(exclusions, list):
        errors.append("Exclusions is not a list")
    else:
        for i, excl in enumerate(exclusions):
            if not isinstance(excl, dict):
                errors.append(f"Exclusion {i} is not a dict")
            elif not excl.get("statement"):
                errors.append(f"Exclusion {i} missing statement")
            elif "order" not in excl:
                errors.append(f"Exclusion {i} missing order")

    return errors


def validate_or_raise(groups: List[Dict[str, Any]]) -> None:
    """Validate all groups and raise ValidationError if any errors found.

    Runs all validations (completeness, consistency, accuracy) on all groups.
    Designed to be used as a gate before database insertion.

    Per CONTEXT.md: "Never insert partial or corrupt data"

    Args:
        groups: List of group dictionaries to validate

    Raises:
        ValidationError: If any validation errors are found

    Returns:
        None if all groups are valid
    """
    all_errors = []

    # Validate each group individually
    for idx, group in enumerate(groups):
        group_errors = validate_group(group)
        for error in group_errors:
            code = group.get("group_code", f"[index {idx}]")
            all_errors.append(f"Group {code}: {error}")

    # Validate consistency across all groups
    consistency_errors = validate_consistency(groups)
    all_errors.extend(consistency_errors)

    if all_errors:
        raise ValidationError(all_errors)
