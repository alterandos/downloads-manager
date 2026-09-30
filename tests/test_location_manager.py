"""
Tests for utils/location_manager — saving new locations to paths.py and
config_locations.py, and updating in-memory objects without a restart.
"""
import sys
import types
import pytest


SAMPLE_PATHS_PY = """\
class DirectoryPaths:
    DOCUMENTS = r'C:\\Users\\test\\Documents'
    DOWNLOADS = r'C:\\Users\\test\\Downloads'
"""

SAMPLE_CONFIG_PY = """\
DEFAULT_LOCATION_KEYS = [
    "DOCUMENTS",
    "DOWNLOADS",
]

INVOICE_LOCATION_KEYS = [
    "PHYSIO_RECEIPTS",
]
"""


# ── name_to_key ────────────────────────────────────────────────────────────────

class TestNameToKey:
    def test_two_word_title_case(self):
        from utils.location_manager import name_to_key
        assert name_to_key("Restaurant Invoices") == "RESTAURANT_INVOICES"

    def test_single_word(self):
        from utils.location_manager import name_to_key
        assert name_to_key("Physio") == "PHYSIO"

    def test_all_lowercase(self):
        from utils.location_manager import name_to_key
        assert name_to_key("physio receipts") == "PHYSIO_RECEIPTS"

    def test_strips_special_characters(self):
        from utils.location_manager import name_to_key
        assert name_to_key("Doctor's Receipts!") == "DOCTORS_RECEIPTS"

    def test_collapses_multiple_spaces(self):
        from utils.location_manager import name_to_key
        assert name_to_key("A  B  C") == "A_B_C"

    def test_already_uppercase_unchanged(self):
        from utils.location_manager import name_to_key
        assert name_to_key("DOCUMENTS") == "DOCUMENTS"


# ── paths.py file manipulation ─────────────────────────────────────────────────

class TestAppendToPathsPy:
    def _setup(self, tmp_path, monkeypatch):
        paths_file = tmp_path / "paths.py"
        paths_file.write_text(SAMPLE_PATHS_PY, encoding="utf-8")
        monkeypatch.setattr("utils.location_manager._PATHS_FILE", str(paths_file))
        return paths_file

    def test_appends_new_key(self, tmp_path, monkeypatch):
        f = self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_paths_py
        assert _append_to_paths_py("RESTAURANT", r"C:\Users\test\Restaurant") is True
        content = f.read_text()
        assert "RESTAURANT" in content
        assert r"C:\Users\test\Restaurant" in content

    def test_new_key_is_inside_class(self, tmp_path, monkeypatch):
        f = self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_paths_py
        _append_to_paths_py("NEW_LOC", r"C:\somewhere")
        lines = f.read_text().splitlines()
        new_line = next((l for l in lines if "NEW_LOC" in l), None)
        assert new_line is not None
        assert new_line.startswith("    "), "Attribute must be indented (inside the class)"

    def test_does_not_duplicate_existing_key(self, tmp_path, monkeypatch):
        f = self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_paths_py
        _append_to_paths_py("DOCUMENTS", r"C:\new\path")
        assert f.read_text().count("DOCUMENTS") == 1

    def test_returns_true_on_duplicate_key(self, tmp_path, monkeypatch):
        self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_paths_py
        assert _append_to_paths_py("DOWNLOADS", r"C:\whatever") is True


# ── config_locations.py file manipulation ─────────────────────────────────────

class TestAppendToConfigLocations:
    def _setup(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config_locations.py"
        config_file.write_text(SAMPLE_CONFIG_PY, encoding="utf-8")
        monkeypatch.setattr("utils.location_manager._CONFIG_LOCATIONS_FILE", str(config_file))
        return config_file

    def test_appends_key_to_default_list(self, tmp_path, monkeypatch):
        f = self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_config_locations
        assert _append_to_config_locations("RESTAURANT", "DEFAULT_LOCATION_KEYS") is True
        assert '"RESTAURANT"' in f.read_text()

    def test_appends_to_correct_list(self, tmp_path, monkeypatch):
        f = self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_config_locations
        _append_to_config_locations("DENTAL", "INVOICE_LOCATION_KEYS")
        # DENTAL must appear AFTER the INVOICE_LOCATION_KEYS declaration
        content = f.read_text()
        invoice_idx = content.index("INVOICE_LOCATION_KEYS")
        dental_idx  = content.index('"DENTAL"')
        assert dental_idx > invoice_idx

    def test_does_not_touch_other_list(self, tmp_path, monkeypatch):
        f = self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_config_locations
        _append_to_config_locations("DENTAL", "INVOICE_LOCATION_KEYS")
        content = f.read_text()
        # DENTAL should not appear in the DEFAULT_LOCATION_KEYS block
        default_block = content.split("INVOICE_LOCATION_KEYS")[0]
        assert '"DENTAL"' not in default_block

    def test_does_not_duplicate_existing_key(self, tmp_path, monkeypatch):
        f = self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_config_locations
        _append_to_config_locations("DOCUMENTS", "DEFAULT_LOCATION_KEYS")
        assert f.read_text().count('"DOCUMENTS"') == 1

    def test_returns_false_for_missing_list(self, tmp_path, monkeypatch):
        self._setup(tmp_path, monkeypatch)
        from utils.location_manager import _append_to_config_locations
        assert _append_to_config_locations("SOMETHING", "NONEXISTENT_KEYS") is False


# ── In-memory update ───────────────────────────────────────────────────────────

class TestUpdateInMemory:
    def test_sets_attribute_on_directory_paths(self, monkeypatch):
        fake_paths = types.ModuleType("paths")
        class FakeDP:
            pass
        fake_paths.DirectoryPaths = FakeDP
        monkeypatch.setitem(sys.modules, "paths", fake_paths)

        from utils.location_manager import _update_in_memory
        _update_in_memory("RESTAURANT", r"C:\test\Restaurant", "DEFAULT_LOCATION_KEYS")

        assert hasattr(FakeDP, "RESTAURANT")
        assert FakeDP.RESTAURANT == r"C:\test\Restaurant"

    def test_appends_to_existing_list_in_place(self, monkeypatch):
        fake_config = types.ModuleType("config_locations")
        test_list = ["DOCUMENTS"]
        fake_config.DEFAULT_LOCATION_KEYS = test_list
        monkeypatch.setitem(sys.modules, "config_locations", fake_config)

        from utils.location_manager import _update_in_memory
        _update_in_memory("RESTAURANT", r"C:\test", "DEFAULT_LOCATION_KEYS")

        # Mutated in-place — all references see the new item
        assert "RESTAURANT" in test_list

    def test_does_not_duplicate_in_memory_key(self, monkeypatch):
        fake_config = types.ModuleType("config_locations")
        test_list = ["DOCUMENTS", "RESTAURANT"]
        fake_config.DEFAULT_LOCATION_KEYS = test_list
        monkeypatch.setitem(sys.modules, "config_locations", fake_config)

        from utils.location_manager import _update_in_memory
        _update_in_memory("RESTAURANT", r"C:\test", "DEFAULT_LOCATION_KEYS")

        assert test_list.count("RESTAURANT") == 1

    def test_handles_missing_paths_module_gracefully(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "paths", None)
        from utils.location_manager import _update_in_memory
        _update_in_memory("X", r"C:\x", "DEFAULT_LOCATION_KEYS")  # must not raise
