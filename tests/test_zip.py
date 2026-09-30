"""
Tests for ZIP inspection, extraction, and the ZIPHandler routing logic.
"""
import os
import zipfile
import pytest


class TestZipContainsExtension:
    def test_detects_h3m_in_heroes_zip(self, heroes_zip):
        from utils.zip_utils import zip_contains_extension
        assert zip_contains_extension(heroes_zip, {".h3m"}) is True

    def test_no_h3m_in_plain_zip(self, plain_zip):
        from utils.zip_utils import zip_contains_extension
        assert zip_contains_extension(plain_zip, {".h3m"}) is False

    def test_multiple_extension_check_returns_true_if_any_match(self, heroes_zip):
        from utils.zip_utils import zip_contains_extension
        assert zip_contains_extension(heroes_zip, {".h3m", ".pdf"}) is True

    def test_extension_check_is_case_insensitive(self, tmp_path):
        zip_path = tmp_path / "upper.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("MAP.H3M", b"content")
        from utils.zip_utils import zip_contains_extension
        assert zip_contains_extension(str(zip_path), {".h3m"}) is True

    def test_empty_zip_returns_false(self, tmp_path):
        zip_path = tmp_path / "empty.zip"
        with zipfile.ZipFile(zip_path, "w"):
            pass
        from utils.zip_utils import zip_contains_extension
        assert zip_contains_extension(str(zip_path), {".h3m"}) is False


class TestExtractAndRename:
    def _rename_fn(self, name: str) -> str:
        return f"[HotA] {name}" if not name.lower().startswith("[hota]") else name

    def test_extracts_h3m_with_hota_prefix(self, heroes_zip, tmp_path, monkeypatch):
        monkeypatch.setattr("ui.prompts.confirm_overwrite", lambda *a, **kw: True)

        from utils.zip_utils import extract_and_rename
        extracted, unknown = extract_and_rename(
            zip_path=heroes_zip,
            target_ext=".h3m",
            dest_dir=str(tmp_path),
            rename_fn=self._rename_fn,
        )

        assert extracted is True
        h3m_files = [f for f in os.listdir(tmp_path) if f.endswith(".h3m")]
        assert len(h3m_files) == 1
        assert h3m_files[0].startswith("[HotA]")

    def test_does_not_double_prefix_already_tagged_maps(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ui.prompts.confirm_overwrite", lambda *a, **kw: True)

        zip_path = tmp_path / "tagged.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("[HotA] existing_map.h3m", b"content")

        dest = tmp_path / "dest"
        dest.mkdir()

        from utils.zip_utils import extract_and_rename
        extract_and_rename(str(zip_path), ".h3m", str(dest), self._rename_fn)

        files = list(dest.iterdir())
        assert len(files) == 1
        assert files[0].name.count("[HotA]") == 1

    def test_plain_zip_extracts_nothing_for_h3m(self, plain_zip, tmp_path, monkeypatch):
        monkeypatch.setattr("ui.prompts.confirm_overwrite", lambda *a, **kw: True)

        from utils.zip_utils import extract_and_rename
        extracted, _ = extract_and_rename(
            zip_path=plain_zip,
            target_ext=".h3m",
            dest_dir=str(tmp_path),
            rename_fn=self._rename_fn,
        )
        assert extracted is False

    def test_unknown_non_txt_files_returned(self, heroes_zip, tmp_path, monkeypatch):
        monkeypatch.setattr("ui.prompts.confirm_overwrite", lambda *a, **kw: True)

        from utils.zip_utils import extract_and_rename
        _, unknown = extract_and_rename(
            zip_path=heroes_zip,
            target_ext=".h3m",
            dest_dir=str(tmp_path),
            rename_fn=self._rename_fn,
        )
        # heroes_zip has readme.txt — txt files are excluded from unknown list
        assert all(not u.endswith(".txt") for u in unknown)

    def test_existing_file_skipped_when_overwrite_declined(self, heroes_zip, tmp_path, monkeypatch):
        # zip_utils imports confirm_overwrite directly — patch at the import site
        monkeypatch.setattr("utils.zip_utils.confirm_overwrite", lambda *a, **kw: False)

        dest = tmp_path / "dest"
        dest.mkdir()
        # Pre-create the destination file
        (dest / "[HotA] Great_Battle.h3m").write_bytes(b"original")

        from utils.zip_utils import extract_and_rename
        extracted, _ = extract_and_rename(
            zip_path=heroes_zip,
            target_ext=".h3m",
            dest_dir=str(dest),
            rename_fn=self._rename_fn,
        )
        assert extracted is False
        # Original should be untouched
        assert (dest / "[HotA] Great_Battle.h3m").read_bytes() == b"original"


class TestZIPHandler:
    def test_heroes_zip_extracts_h3m(self, heroes_zip, tmp_path, monkeypatch):
        import paths
        monkeypatch.setattr(paths.DirectoryPaths, "HEROES_MAPS", str(tmp_path))
        monkeypatch.setattr("ui.prompts.confirm_overwrite", lambda *a, **kw: True)
        monkeypatch.setattr("ui.prompts.confirm_delete_zip_no_extracted", lambda *a, **kw: False)

        from handlers.zip import ZIPHandler
        class _Ev:
            src_path = heroes_zip
        ZIPHandler().handle(_Ev())

        extracted = [f for f in os.listdir(tmp_path) if f.endswith(".h3m")]
        assert len(extracted) == 1
        assert extracted[0].startswith("[HotA]")

    def test_plain_zip_does_not_touch_dest_folder(self, plain_zip, tmp_path, monkeypatch):
        import paths
        dest = tmp_path / "maps"
        dest.mkdir()
        monkeypatch.setattr(paths.DirectoryPaths, "HEROES_MAPS", str(dest))

        from handlers.zip import ZIPHandler
        class _Ev:
            src_path = plain_zip
        ZIPHandler().handle(_Ev())

        assert list(dest.iterdir()) == []

    def test_heroes_zip_deleted_after_extraction(self, heroes_zip, tmp_path, monkeypatch):
        import paths
        monkeypatch.setattr(paths.DirectoryPaths, "HEROES_MAPS", str(tmp_path))
        monkeypatch.setattr("ui.prompts.confirm_overwrite", lambda *a, **kw: True)
        monkeypatch.setattr("ui.prompts.confirm_delete_zip_no_extracted", lambda *a, **kw: False)

        from handlers.zip import ZIPHandler
        class _Ev:
            src_path = heroes_zip
        ZIPHandler().handle(_Ev())

        assert not os.path.exists(heroes_zip), "ZIP should be deleted after successful extraction"
