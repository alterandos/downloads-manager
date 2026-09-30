"""
LLM-based invoice classification via a local Ollama model.

NOT YET IMPLEMENTED — returns (None, 0.0) as a stub.
See backlog.md for full implementation requirements.

When implemented, this module will:
  - POST extracted PDF text to a locally running Ollama instance (localhost:11434)
  - Receive a JSON response with {"type": "<invoice_type>", "confidence": 0.0–1.0}
  - Return (invoice_type, confidence), or (None, 0.0) on any failure

The caller (classifier.py) already handles a (None, 0.0) response gracefully —
the user sees an unpopulated picker with no pre-selected suggestion.
"""
from utils.logging_setup import get_logger

logger = get_logger(__name__)


def classify(text: str | None) -> tuple[str | None, float]:
    """
    Classify invoice type using a local LLM (Ollama).

    Returns (invoice_type, confidence).
    Stub: always returns (None, 0.0) until Ollama integration is implemented.
    """
    # TODO: implement — see backlog.md
    logger.debug("llm_client.classify called (stub — returning None)")
    return None, 0.0
