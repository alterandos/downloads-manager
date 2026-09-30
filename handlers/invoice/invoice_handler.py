"""Orchestrates invoice classification, user confirmation, and file routing."""
import os
from .classifier import classify
from .pdf_extractor import extract_text
from config_locations import resolve_locations, INVOICE_LOCATION_KEYS, suggested_invoice_path
from utils.file_ops import move_file
from ui.location_selector import select_location
from utils.logging_setup import get_logger
from utils.skip_store import mark_skipped

logger = get_logger(__name__)

# Below this confidence, skip straight to asking the user (still with a suggestion if available)
_FAST_PATH_THRESHOLD = 1.0


def handle_invoice(event) -> None:
    """Classify an invoice PDF and prompt the user to confirm the destination."""
    filename = os.path.basename(event.src_path)

    # Stage 1: try filename alone — no disk read needed
    invoice_type, confidence = classify(filename)

    # Stage 2: read PDF text only if filename gave no result
    if invoice_type is None or confidence < _FAST_PATH_THRESHOLD:
        pdf_text = extract_text(event.src_path)
        invoice_type, confidence = classify(filename, pdf_text)

    logger.info(f"Invoice classification: type={invoice_type!r} confidence={confidence:.2f} | {filename}")

    # Resolve the suggested destination path (may be None)
    suggestion = suggested_invoice_path(invoice_type)

    options = resolve_locations(INVOICE_LOCATION_KEYS)

    title_lines = [f"Invoice: {filename}"]
    if invoice_type:
        title_lines.append(f"Suggested type: {invoice_type.replace('_', ' ').title()}")

    dest = select_location(
        options,
        title="\n".join(title_lines),
        allow_browse=True,
        suggestion=suggestion,
        save_to_list="INVOICE_LOCATION_KEYS",
    )

    if dest:
        move_file(event.src_path, dest)
        logger.info(f"Invoice moved to: {dest}")
    else:
        logger.info(f"Invoice routing skipped by user: {filename}")
        mark_skipped(event.src_path)
