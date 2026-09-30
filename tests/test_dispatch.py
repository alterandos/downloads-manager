"""
Tests for file dispatch routing.

Covers: HANDLER_REGISTRY, IGNORED_EXTENSIONS, _dispatch_file() routing,
and exception isolation (a crashing handler should not propagate to the caller).
"""
import pytest


class TestHandlerRegistry:
    def test_pdf_mapped_to_pdf_handler(self):
        from config import HANDLER_REGISTRY
        from handlers.pdf import PDFHandler
        assert HANDLER_REGISTRY[".pdf"] is PDFHandler

    def test_zip_mapped_to_zip_handler(self):
        from config import HANDLER_REGISTRY
        from handlers.zip import ZIPHandler
        assert HANDLER_REGISTRY[".zip"] is ZIPHandler

    def test_guitar_pro_extensions_all_mapped(self):
        from config import HANDLER_REGISTRY
        from handlers.gp import GPHandler
        for ext in (".gpx", ".gp4", ".gp5"):
            assert HANDLER_REGISTRY[ext] is GPHandler, f"{ext} not in registry"

    def test_default_handler_not_in_registry(self):
        # DefaultFileHandler is the fallback — it must NOT be an explicit registry entry
        from config import HANDLER_REGISTRY
        from handlers.default import DefaultFileHandler
        assert DefaultFileHandler not in HANDLER_REGISTRY.values()


class TestIgnoredExtensions:
    def test_common_in_progress_extensions_are_ignored(self):
        from config import IGNORED_EXTENSIONS
        for ext in (".crdownload", ".part", ".tmp", ".download"):
            assert ext in IGNORED_EXTENSIONS, f"{ext} should be in IGNORED_EXTENSIONS"

    def test_system_files_are_ignored(self):
        from config import IGNORED_EXTENSIONS
        for ext in (".lnk", ".exe", ".ini"):
            assert ext in IGNORED_EXTENSIONS, f"{ext} should be in IGNORED_EXTENSIONS"


class TestDispatchRouting:
    def test_ignored_extension_never_reaches_any_handler(self, tmp_path, monkeypatch):
        f = tmp_path / "download.crdownload"
        f.write_text("partial")

        handled = []
        monkeypatch.setattr("handlers.default.DefaultFileHandler.handle",
                            lambda self, e: handled.append(e))

        from main import _dispatch_file
        _dispatch_file(str(f))
        assert handled == [], ".crdownload should be silently skipped"

    def test_unknown_extension_reaches_default_handler(self, tmp_path, monkeypatch):
        f = tmp_path / "mystery.xyzabc"
        f.write_text("unknown")

        handled = []
        monkeypatch.setattr("handlers.default.DefaultFileHandler.handle",
                            lambda self, e: handled.append(e.src_path))

        from main import _dispatch_file
        _dispatch_file(str(f))
        assert len(handled) == 1
        assert "mystery.xyzabc" in handled[0]

    def test_pdf_reaches_pdf_handler(self, tmp_path, monkeypatch):
        f = tmp_path / "report.pdf"
        f.write_bytes(b"%PDF-1.4")

        handled = []
        monkeypatch.setattr("handlers.pdf.PDFHandler.handle",
                            lambda self, e: handled.append(e.src_path))

        from main import _dispatch_file
        _dispatch_file(str(f))
        assert len(handled) == 1

    def test_zip_reaches_zip_handler(self, heroes_zip, monkeypatch):
        handled = []
        monkeypatch.setattr("handlers.zip.ZIPHandler.handle",
                            lambda self, e: handled.append(e.src_path))

        from main import _dispatch_file
        _dispatch_file(heroes_zip)
        assert len(handled) == 1

    def test_gpx_reaches_gp_handler(self, tmp_path, monkeypatch):
        f = tmp_path / "song.gpx"
        f.write_bytes(b"fake gpx")

        handled = []
        monkeypatch.setattr("handlers.gp.GPHandler.handle",
                            lambda self, e: handled.append(e.src_path))

        from main import _dispatch_file
        _dispatch_file(str(f))
        assert len(handled) == 1

    def test_nonexistent_file_is_silently_skipped(self, tmp_path, monkeypatch):
        handled = []
        monkeypatch.setattr("handlers.default.DefaultFileHandler.handle",
                            lambda self, e: handled.append(e))

        from main import _dispatch_file
        _dispatch_file(str(tmp_path / "ghost.pdf"))
        # File does not exist, but _dispatch_file does not guard existence —
        # it lets the handler fail. This test verifies no unhandled exception bubbles up.


class TestExceptionIsolation:
    def test_handler_error_does_not_propagate(self, tmp_path, monkeypatch):
        """A handler that raises (and whose handle_error also raises) must not crash _dispatch_file."""
        f = tmp_path / "bad.pdf"
        f.write_bytes(b"%PDF-1.4")

        monkeypatch.setattr("handlers.pdf.PDFHandler.handle",
                            lambda self, e: (_ for _ in ()).throw(RuntimeError("boom")))
        monkeypatch.setattr("handlers.pdf.PDFHandler.handle_error",
                            lambda self, e, err: (_ for _ in ()).throw(err))

        from main import _dispatch_file
        _dispatch_file(str(f))  # must not raise
