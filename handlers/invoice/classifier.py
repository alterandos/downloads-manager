"""
Tiered invoice classification pipeline.

Stages (each only runs if the previous returned no confident match):
  1. Filename keyword match  → confidence 1.0
  2. PDF text keyword match  → confidence 0.85
  3. Local LLM (Ollama stub) → confidence from model, currently always 0.0
"""
from .keyword_rules import FILENAME_KEYWORDS, TEXT_KEYWORDS
from . import llm_client


def classify(filename: str, pdf_text: str | None = None) -> tuple[str | None, float]:
    """
    Return (invoice_type, confidence) for a given filename and optional PDF text.

    invoice_type is a key from keyword_rules (e.g. 'physio'), or None if unknown.
    confidence is 0.0–1.0.
    """
    # Stage 1: filename keywords
    match = _keyword_match(filename.lower(), FILENAME_KEYWORDS)
    if match:
        return match, 1.0

    # Stage 2: PDF text keywords
    if pdf_text:
        match = _keyword_match(pdf_text.lower(), TEXT_KEYWORDS)
        if match:
            return match, 0.85

    # Stage 3: LLM fallback (stub returns None, 0.0)
    return llm_client.classify(pdf_text)


def _keyword_match(text: str, rules: dict[str, list[str]]) -> str | None:
    for invoice_type, keywords in rules.items():
        if any(kw.lower() in text for kw in keywords):
            return invoice_type
    return None
