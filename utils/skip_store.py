"""
Persistent record of files the user chose to Skip.

Skipped files are left in Downloads and are never prompted for again, across
restarts. Entries for files that no longer exist are pruned on load.
"""
import json
import os
import threading
from utils.logging_setup import get_logger

logger = get_logger(__name__)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
STORE_FILE = os.path.join(_PROJECT_ROOT, "data", "skipped_files.json")

_lock = threading.Lock()
_skipped = None  # set of normalised paths, loaded lazily


def _key(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def _load() -> set:
    global _skipped
    if _skipped is None:
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except FileNotFoundError:
            entries = []
        except Exception as e:
            logger.warning(f"skip_store: could not read {STORE_FILE}: {e}")
            entries = []
        _skipped = {p for p in entries if os.path.exists(p)}
    return _skipped


def _save() -> None:
    try:
        os.makedirs(os.path.dirname(STORE_FILE), exist_ok=True)
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(_skipped), f, indent=2)
    except Exception as e:
        logger.error(f"skip_store: could not write {STORE_FILE}: {e}")


def mark_skipped(path: str) -> None:
    """Remember that the user skipped this file."""
    with _lock:
        _load().add(_key(path))
        _save()
    logger.info(f"Remembered skip: {os.path.basename(path)}")


def is_skipped(path: str) -> bool:
    with _lock:
        return _key(path) in _load()


def reset() -> None:
    """Drop the in-memory cache so the next call reloads from STORE_FILE (used by tests)."""
    global _skipped
    with _lock:
        _skipped = None
