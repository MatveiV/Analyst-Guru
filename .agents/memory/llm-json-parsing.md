---
name: LLM JSON parsing
description: LLMs often return JSON wrapped in markdown code fences; safe parsing strategy
---

LLMs (Anthropic Claude, OpenAI GPT) often wrap JSON in markdown fences (```json ... ```) even when instructed not to.

**Rule:** Always strip markdown fences before JSON.parse, then fall back to regex extraction of `{...}` block.

**Why:** Direct `json.loads()` fails on fenced output, causing silent failures if not handled.

**How to apply:** Use `safe_parse_json()` from `backend/services/ai_service.py`:
1. Strip leading/trailing whitespace
2. If starts with ```, split on newlines and drop first/last lines
3. Try `json.loads()`
4. On failure, regex search for `\{.*\}` with DOTALL flag
5. Return `None` if all fail — caller uses fallback dict with `needs_review=True`
