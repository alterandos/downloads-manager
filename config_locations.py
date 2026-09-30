"""
Location groups for UI pickers.

Lists here contain attribute name strings from DirectoryPaths. They are resolved
to (label, path) tuples at runtime by resolve_locations() so this file stays
committed to git while actual paths live in the gitignored paths.py.

To add a new destination option: add the DirectoryPaths attribute name to the
relevant list, and make sure the attribute exists in your paths.py.
"""
from typing import Optional
from paths import DirectoryPaths

# ── Invoice destinations ───────────────────────────────────────────────────────

# All locations shown in the invoice destination picker
INVOICE_LOCATION_KEYS = [
    "PHYSIO_RECEIPTS",
    # "DENTAL_RECEIPTS",
    # "GENERAL_RECEIPTS",
]

# Maps classifier invoice_type strings → DirectoryPaths attribute names.
# Used to derive the suggested destination when the classifier returns a type.
INVOICE_TYPE_TO_KEY: dict[str, str] = {
    "physio": "PHYSIO_RECEIPTS",
    # "dental": "DENTAL_RECEIPTS",
}

# ── Default / fallback destinations ───────────────────────────────────────────

# Shown in the DefaultFileHandler picker for unrecognised file types
DEFAULT_LOCATION_KEYS = [
    "DOCUMENTS",
    "DOWNLOADS",
    # Add any other commonly useful destinations here
    "SPECIAL_CONSIDERATION",
    "OA_RESEARCH_READINGS",
    "STATEMENTS",
    "HOT_CHOCOLATE",
    "FUNNY_SHIT",
]


# ── Resolution helper ──────────────────────────────────────────────────────────

def resolve_locations(keys: list[str]) -> list[tuple[str, str]]:
    """Convert a list of DirectoryPaths attribute names to (label, path) pairs.

    Keys that don't exist on DirectoryPaths are skipped with a warning.
    Label is derived from the key: PHYSIO_RECEIPTS → 'Physio Receipts'.
    """
    from utils.logging_setup import get_logger
    logger = get_logger(__name__)

    result = []
    for key in keys:
        path = getattr(DirectoryPaths, key, None)
        if path is None:
            logger.warning(f"config_locations: DirectoryPaths has no attribute '{key}' — skipping")
            continue
        label = key.replace('_', ' ').title()
        result.append((label, path))
    return result


def suggested_invoice_path(invoice_type: Optional[str]) -> Optional[str]:
    """Return the DirectoryPaths value for a given invoice_type, or None."""
    if invoice_type is None:
        return None
    key = INVOICE_TYPE_TO_KEY.get(invoice_type)
    if key is None:
        return None
    return getattr(DirectoryPaths, key, None)
