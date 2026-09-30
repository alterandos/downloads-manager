"""
Persist a user-chosen folder as a named location in paths.py and config_locations.py,
and immediately make it available in the running session without a restart.

Writing approach
----------------
paths.py         — appends a new class attribute to DirectoryPaths (raw string literal)
config_locations — appends the key string to the named list variable

In-memory update
----------------
Rather than reloading modules (which breaks references captured by `from x import y`),
we mutate the live objects directly via sys.modules:
  - setattr(DirectoryPaths, key, path) so resolve_locations() sees the new attribute
  - target_list.append(key)             so callers holding a reference to the list see it too
"""
import os
import re
import sys
from utils.logging_setup import get_logger

logger = get_logger(__name__)

# Resolve file paths relative to the project root (one level up from utils/)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATHS_FILE = os.path.join(_PROJECT_ROOT, "paths.py")
_CONFIG_LOCATIONS_FILE = os.path.join(_PROJECT_ROOT, "config_locations.py")


def name_to_key(name: str) -> str:
    """Convert a human label to a DirectoryPaths-style constant name.

    "Restaurant Invoices" → "RESTAURANT_INVOICES"
    """
    key = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    key = re.sub(r"\s+", "_", key.strip())
    return key.upper()


def save_location(name: str, path: str, list_name: str) -> bool:
    """
    Save a new location so it appears in future sessions and immediately in this one.

    name      — human label the user typed, e.g. "Restaurant Invoices"
    path      — absolute folder path chosen via browse dialog
    list_name — variable name in config_locations.py to append to,
                e.g. "DEFAULT_LOCATION_KEYS" or "INVOICE_LOCATION_KEYS"

    Returns True on success, False if either file write failed.
    """
    key = name_to_key(name)
    # Normalise to Windows backslashes for paths.py consistency
    norm_path = os.path.normpath(path)

    ok_paths  = _append_to_paths_py(key, norm_path)
    ok_config = _append_to_config_locations(key, list_name)

    if ok_paths and ok_config:
        _update_in_memory(key, norm_path, list_name)
        logger.info(f"Saved location: {key} = {norm_path!r} → {list_name}")

    return ok_paths and ok_config


def _append_to_paths_py(key: str, path: str) -> bool:
    """Append `    KEY = r'path'` after the last attribute in DirectoryPaths."""
    try:
        with open(_PATHS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Bail out early if key already exists
        if any(re.match(rf"^\s+{key}\s*=", line) for line in lines):
            logger.info(f"paths.py: {key} already exists, skipping write")
            return True

        # Find the last indented class-attribute line
        last_attr_idx = None
        for i, line in enumerate(lines):
            if re.match(r"^    \w+ = ", line):
                last_attr_idx = i

        if last_attr_idx is None:
            logger.error("paths.py: could not find any DirectoryPaths attributes")
            return False

        # Ensure the preceding line ends with a newline before inserting after it
        if not lines[last_attr_idx].endswith("\n"):
            lines[last_attr_idx] += "\n"

        new_line = f"    {key} = r'{path}'\n"
        lines.insert(last_attr_idx + 1, new_line)

        with open(_PATHS_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)

        logger.info(f"paths.py: appended {key} = r'{path}'")
        return True

    except Exception as e:
        logger.error(f"Failed to write to paths.py: {e}")
        return False


def _append_to_config_locations(key: str, list_name: str) -> bool:
    """Append `    "KEY",` inside the named list in config_locations.py."""
    try:
        with open(_CONFIG_LOCATIONS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Bail out if key is already present in the file
        if f'"{key}"' in content or f"'{key}'" in content:
            logger.info(f"config_locations.py: {key} already present, skipping write")
            return True

        # Match the list: LIST_NAME = [\n...\n]
        pattern = rf"({re.escape(list_name)}\s*=\s*\[)(.*?)(\])"
        m = re.search(pattern, content, re.DOTALL)
        if not m:
            logger.error(f"config_locations.py: could not find list '{list_name}'")
            return False

        before_bracket = content[: m.start(3)]
        after_bracket  = content[m.start(3):]

        # Ensure the entry goes on its own indented line
        new_entry = f'    "{key}",\n'
        if not before_bracket.endswith("\n"):
            new_entry = "\n" + new_entry

        new_content = before_bracket + new_entry + after_bracket

        with open(_CONFIG_LOCATIONS_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

        logger.info(f"config_locations.py: appended '{key}' to {list_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to write to config_locations.py: {e}")
        return False


def _update_in_memory(key: str, path: str, list_name: str) -> None:
    """Mutate live objects so the new location is visible without a restart."""
    paths_mod = sys.modules.get("paths")
    if paths_mod and hasattr(paths_mod, "DirectoryPaths"):
        setattr(paths_mod.DirectoryPaths, key, path)

    config_mod = sys.modules.get("config_locations")
    if config_mod:
        target_list = getattr(config_mod, list_name, None)
        if isinstance(target_list, list) and key not in target_list:
            target_list.append(key)
