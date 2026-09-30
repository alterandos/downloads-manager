"""
Tests for skip memory and suppression of read-only filesystem events.
"""
import os


class TestSkipStore:
    def test_skip_persists_across_reload(self, tmp_path, isolated_skip_store):
        f = tmp_path / "doc.docx"
        f.write_text("x")
        isolated_skip_store.mark_skipped(str(f))
        isolated_skip_store.reset()
        assert isolated_skip_store.is_skipped(str(f))

    def test_missing_files_pruned_on_load(self, tmp_path, isolated_skip_store):
        f = tmp_path / "gone.docx"
        f.write_text("x")
        isolated_skip_store.mark_skipped(str(f))
        f.unlink()
        isolated_skip_store.reset()
        assert not isolated_skip_store.is_skipped(str(f))

    def test_default_handler_skip_prevents_future_dispatch(self, tmp_path, monkeypatch):
        f = tmp_path / "mystery.xyzabc"
        f.write_text("unknown")

        prompts = []
        def fake_select(*a, **kw):
            prompts.append(1)
            return None
        monkeypatch.setattr("handlers.default.select_location", fake_select)

        from main import _dispatch_file
        _dispatch_file(str(f))
        _dispatch_file(str(f))
        assert len(prompts) == 1, "Skipped file should not be prompted again"


class TestReadOnlyEventsIgnored:
    def test_unchanged_existing_file_not_scheduled(self, tmp_path, monkeypatch):
        import main
        f = tmp_path / "old.pdf"
        f.write_bytes(b"%PDF-1.4")
        monkeypatch.setattr(main, "_file_signatures", {})
        monkeypatch.setattr(main, "_pending_timers", {})
        main._snapshot_existing_files(str(tmp_path))

        main.DownloadHandler()._schedule(str(f), "on_modified")  # e.g. Explorer read it
        assert str(f) not in main._pending_timers

    def test_changed_file_is_scheduled(self, tmp_path, monkeypatch):
        import main
        f = tmp_path / "old.pdf"
        f.write_bytes(b"%PDF-1.4")
        monkeypatch.setattr(main, "_file_signatures", {})
        monkeypatch.setattr(main, "_pending_timers", {})
        main._snapshot_existing_files(str(tmp_path))

        f.write_bytes(b"%PDF-1.4 more content")
        main.DownloadHandler()._schedule(str(f), "on_modified")
        assert str(f) in main._pending_timers
        main._pending_timers[str(f)].cancel()
