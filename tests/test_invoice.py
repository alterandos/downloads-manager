"""
Tests for the invoice classification pipeline.

Covers: keyword matching (filename + text), LLM stub, PDF text extraction,
and the invoice_handler routing logic.
"""
import pytest


class TestClassifierFilenameKeywords:
    def test_physio_in_filename(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("physio_invoice_jan2024.pdf")
        assert t == "physio" and conf == 1.0

    def test_physiotherapy_in_filename(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("Physiotherapy Receipt.pdf")
        assert t == "physio" and conf == 1.0

    def test_filename_match_is_case_insensitive(self):
        from handlers.invoice.classifier import classify
        t, _ = classify("PHYSIO INVOICE 2024.pdf")
        assert t == "physio"

    def test_generic_invoice_filename_returns_none(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("invoice_20240101.pdf")
        assert t is None and conf == 0.0


class TestClassifierTextKeywords:
    def test_physiotherapy_in_text(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("invoice.pdf", "Thank you for your physiotherapy appointment")
        assert t == "physio" and conf == 0.85

    def test_physiotherapist_in_text(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("invoice.pdf", "Your physiotherapist has completed the assessment")
        assert t == "physio" and conf == 0.85

    def test_filename_match_takes_priority_over_text(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("physio_invoice.pdf", "unrelated office supplies purchase")
        assert t == "physio" and conf == 1.0  # filename wins

    def test_irrelevant_text_returns_none(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("invoice.pdf", "purchase of office supplies and stationery items")
        assert t is None and conf == 0.0

    def test_no_text_provided_falls_through_to_llm_stub(self):
        from handlers.invoice.classifier import classify
        t, conf = classify("invoice.pdf", None)
        assert t is None and conf == 0.0


class TestLLMStub:
    def test_returns_none_with_text(self):
        from handlers.invoice.llm_client import classify
        t, conf = classify("some physiotherapy invoice text")
        assert t is None and conf == 0.0

    def test_returns_none_with_no_text(self):
        from handlers.invoice.llm_client import classify
        t, conf = classify(None)
        assert t is None and conf == 0.0


class TestPDFExtractor:
    def test_nonexistent_file_returns_none(self):
        from handlers.invoice.pdf_extractor import extract_text
        assert extract_text("/nonexistent/path/invoice.pdf") is None

    def test_non_pdf_bytes_return_none(self, tmp_path):
        f = tmp_path / "fake.pdf"
        f.write_bytes(b"this is not a pdf")
        from handlers.invoice.pdf_extractor import extract_text
        # Should handle gracefully — either None or empty-string treated as None
        result = extract_text(str(f))
        assert result is None

    def test_extracts_text_from_real_pdf(self, invoice_pdf):
        from handlers.invoice.pdf_extractor import extract_text
        text = extract_text(invoice_pdf)
        assert text is not None
        assert len(text) > 0
        assert "physiotherapy" in text.lower() or "PHYSIOTHERAPY" in text

    def test_text_truncated_to_max_chars(self, tmp_path):
        """Text longer than MAX_CHARS should be truncated."""
        try:
            from fpdf import FPDF
        except ImportError:
            pytest.skip("fpdf2 not installed")

        pdf_path = tmp_path / "long.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=8)
        # Fill with repeated text well beyond 2000 chars
        for _ in range(100):
            pdf.cell(200, 5, txt="A" * 50, new_x="LMARGIN", new_y="NEXT")
        pdf.output(str(pdf_path))

        from handlers.invoice.pdf_extractor import extract_text, MAX_CHARS
        text = extract_text(str(pdf_path))
        assert text is not None
        assert len(text) <= MAX_CHARS


class TestInvoiceHandlerRouting:
    def test_physio_filename_produces_physio_suggestion(self, tmp_path, monkeypatch):
        """A filename with 'physio' should produce the physio destination as the suggestion."""
        f = tmp_path / "physio_invoice_jan.pdf"
        f.write_bytes(b"%PDF-1.4")

        captured = {}
        def fake_select(options, title="", suggestion=None, **kw):
            captured["suggestion"] = suggestion
            return None  # user skips

        # Patch at the import site — invoice_handler imports select_location directly
        monkeypatch.setattr("handlers.invoice.invoice_handler.select_location", fake_select)
        monkeypatch.setattr("handlers.invoice.invoice_handler.extract_text", lambda p: None)

        from handlers.invoice.invoice_handler import handle_invoice
        class _Ev:
            src_path = str(f)
        handle_invoice(_Ev())

        from config_locations import suggested_invoice_path
        assert captured.get("suggestion") == suggested_invoice_path("physio")

    def test_unknown_invoice_produces_no_suggestion(self, tmp_path, monkeypatch):
        f = tmp_path / "invoice_0001.pdf"
        f.write_bytes(b"%PDF-1.4")

        captured = {}
        def fake_select(options, title="", suggestion=None, **kw):
            captured["suggestion"] = suggestion
            return None

        monkeypatch.setattr("handlers.invoice.invoice_handler.select_location", fake_select)
        monkeypatch.setattr("handlers.invoice.invoice_handler.extract_text", lambda p: None)

        from handlers.invoice.invoice_handler import handle_invoice
        class _Ev:
            src_path = str(f)
        handle_invoice(_Ev())

        assert captured.get("suggestion") is None

    def test_selected_destination_causes_file_move(self, tmp_path, monkeypatch):
        f = tmp_path / "physio_invoice.pdf"
        f.write_bytes(b"%PDF-1.4")
        dest_dir = tmp_path / "receipts"
        dest_dir.mkdir()

        monkeypatch.setattr("handlers.invoice.invoice_handler.select_location",
                            lambda *a, **kw: str(dest_dir))
        monkeypatch.setattr("handlers.invoice.invoice_handler.extract_text", lambda p: None)

        from handlers.invoice.invoice_handler import handle_invoice
        class _Ev:
            src_path = str(f)
        handle_invoice(_Ev())

        assert not f.exists(), "Original file should have been moved"
        assert (dest_dir / "physio_invoice.pdf").exists(), "File should be in dest_dir"

    def test_skipped_destination_leaves_file_in_place(self, tmp_path, monkeypatch):
        f = tmp_path / "invoice_unknown.pdf"
        f.write_bytes(b"%PDF-1.4")

        monkeypatch.setattr("handlers.invoice.invoice_handler.select_location", lambda *a, **kw: None)
        monkeypatch.setattr("handlers.invoice.invoice_handler.extract_text", lambda p: None)

        from handlers.invoice.invoice_handler import handle_invoice
        class _Ev:
            src_path = str(f)
        handle_invoice(_Ev())

        assert f.exists(), "File should remain when user skips"
