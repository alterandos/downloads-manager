"""
Shared fixtures for the Downloads Manager test suite.
"""
import sys
import os
import zipfile
import pytest

# Put the project root on sys.path so all project modules are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── File-creation helpers ──────────────────────────────────────────────────────

def _make_zip(path, files: dict) -> str:
    """Create a ZIP at path with {entry_name: content} entries."""
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content if isinstance(content, bytes) else content.encode())
    return str(path)


# ── File fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def heroes_zip(tmp_path):
    """A ZIP containing a .h3m Heroes of Might & Magic map."""
    return _make_zip(tmp_path / "heroes_maps.zip", {
        "Great_Battle.h3m": b"fake h3m binary content",
        "readme.txt": "Contains heroes maps",
    })


@pytest.fixture
def plain_zip(tmp_path):
    """A ZIP with no .h3m files."""
    return _make_zip(tmp_path / "plain.zip", {
        "document.pdf": b"%PDF-1.4 fake",
        "image.png": b"\x89PNG fake",
    })


@pytest.fixture
def invoice_pdf(tmp_path):
    """
    A real PDF file containing physiotherapy text, usable by pdfplumber.
    Requires fpdf2 — test is automatically skipped if not installed.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        pytest.skip("fpdf2 not installed: pip install fpdf2")

    pdf_path = tmp_path / "physio_invoice_2024.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="PHYSIOTHERAPY INVOICE", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, txt="Patient received physiotherapy treatment.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, txt="Physiotherapist: Jane Smith", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(pdf_path))
    return str(pdf_path)


@pytest.fixture
def generic_invoice_pdf(tmp_path):
    """A PDF labelled 'invoice' with no keyword clues for type."""
    try:
        from fpdf import FPDF
    except ImportError:
        pytest.skip("fpdf2 not installed: pip install fpdf2")

    pdf_path = tmp_path / "invoice_20240101.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="INVOICE", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, txt="For services rendered.", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(pdf_path))
    return str(pdf_path)


# ── UI suppression fixture ─────────────────────────────────────────────────────

@pytest.fixture
def no_ui(monkeypatch):
    """
    Patch every UI call to be a headless no-op.
    By default:
      - select_location returns None  (user skipped)
      - ask_yes_no      returns True  (user said yes)
      - confirm_*       return True

    Override per-test with monkeypatch after requesting this fixture, e.g.:
      monkeypatch.setattr("ui.location_selector.select_location", lambda *a, **kw: "/some/path")
    """
    monkeypatch.setattr("ui.location_selector.select_location",
                        lambda *a, **kw: None)
    monkeypatch.setattr("ui.ctk_utils.ask_yes_no",
                        lambda *a, **kw: True)
    monkeypatch.setattr("ui.ctk_utils.show_info",   lambda *a, **kw: None)
    monkeypatch.setattr("ui.ctk_utils.show_error",  lambda *a, **kw: None)
    monkeypatch.setattr("ui.prompts.confirm_overwrite",
                        lambda *a, **kw: True)
    monkeypatch.setattr("ui.prompts.confirm_delete_zip_no_extracted",
                        lambda *a, **kw: True)


# ── Skip-store isolation ───────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_skip_store(tmp_path, monkeypatch):
    """Point the skip store at a temp file so tests never touch the real one."""
    import utils.skip_store as skip_store
    monkeypatch.setattr(skip_store, "STORE_FILE", str(tmp_path / "skipped_files.json"))
    skip_store.reset()
    yield skip_store
    skip_store.reset()
