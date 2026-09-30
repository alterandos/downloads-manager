"""
Invoice type classification rules.

To add a new invoice type:
  1. Add an entry to FILENAME_KEYWORDS with keywords likely in the filename.
  2. Add an entry to TEXT_KEYWORDS with keywords likely inside the PDF itself.
  3. Add the type → DirectoryPaths key mapping in config_locations.INVOICE_TYPE_TO_KEY.
  4. Make sure the destination path exists in your paths.py.

Keys must match the type strings used in config_locations.INVOICE_TYPE_TO_KEY.
"""

# Matched against the filename (case-insensitive substring match)
FILENAME_KEYWORDS: dict[str, list[str]] = {
    "physio": ["physio", "physiotherapy"],
    # "dental": ["dental", "dentist"],
    # "gp": ["gp", "general practitioner"],
}

# Matched against extracted PDF text (case-insensitive substring match).
# These are checked only when filename matching fails.
TEXT_KEYWORDS: dict[str, list[str]] = {
    "physio": [
        "physiotherapy",
        "physiotherapist",
        "exercise physiology",
        "manual therapy",
        "musculoskeletal",
    ],
    # "dental": ["dental", "dentist", "oral health", "tooth", "teeth"],
}
