"""Extract plain text from a PDF for classification purposes."""
from utils.logging_setup import get_logger

logger = get_logger(__name__)

MAX_CHARS = 2000


def extract_text(pdf_path: str) -> str | None:
    """Return up to MAX_CHARS of text from the start of a PDF, or None on failure."""
    try:
        import pdfplumber
    except ImportError:
        logger.warning("pdfplumber not installed — PDF text extraction unavailable")
        return None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
                if len(text) >= MAX_CHARS:
                    break
            return text[:MAX_CHARS] if text.strip() else None
    except Exception as e:
        logger.warning(f"Failed to extract text from {pdf_path}: {e}")
        return None
