# Backlog

## LLM Invoice Classification (Ollama)

**Stub location:** `handlers/invoice/llm_client.py`
**Integration point:** `handlers/invoice/classifier.py` — Tier 3 already calls `llm_client.classify(pdf_text)`.
No changes needed to the classifier interface when implementing this.

### Goal
When keyword-based classification fails to identify an invoice type, send extracted PDF text to a
local LLM for classification. The result is presented to the user as a suggestion in the location
picker — it is never silently auto-routed.

### Runtime requirements
- **Ollama** must be installed and running locally (default: `http://localhost:11434`)
- Recommended model: `phi3:mini` (fast, small) or `gemma2:2b` (slightly better accuracy)
- The app must degrade gracefully if Ollama is not running — return `(None, 0.0)` and fall through
  to the user prompt with no suggestion

### Function signature (already defined)
```python
# handlers/invoice/llm_client.py
def classify(text: str | None) -> tuple[str | None, float]:
    """Returns (invoice_type, confidence). invoice_type is None if classification fails."""
```
- `invoice_type` must be one of the keys in `keyword_rules.FILENAME_KEYWORDS`, or `None`
- `confidence` is a float 0.0–1.0

### Prompt design
The prompt should:
1. List the known invoice types and their example keywords (read from `keyword_rules`)
2. Ask the model to pick the most likely type or respond "unknown"
3. Request a brief reason (for logging only, not shown to user)
4. Return a structured JSON response for reliable parsing, e.g.:
   ```json
   {"type": "physio", "confidence": 0.87, "reason": "mentions physiotherapy clinic"}
   ```

### Error handling
- **Timeout:** if Ollama doesn't respond within ~5s, return `(None, 0.0)`
- **Parse failure:** log warning, return `(None, 0.0)`
- **Connection error:** log warning once per session (not per file), return `(None, 0.0)`

### Dependencies to add to `requirements.in`
- `ollama` (official Python client) — simplest option
- OR `httpx` for direct HTTP calls to `localhost:11434/api/generate`

### Testing checklist
- [ ] Unit test: mock Ollama HTTP response, verify correct `(type, confidence)` returned
- [ ] Unit test: Ollama timeout → returns `(None, 0.0)` without raising
- [ ] Unit test: malformed JSON response → returns `(None, 0.0)` without raising
- [ ] Integration test: real Ollama running, sample physio invoice PDF → classified correctly
- [ ] Integration test: Ollama not running → app continues normally, user sees unpopulated picker
