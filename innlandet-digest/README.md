# Innlandet Public Announcements Digest – Walking Skeleton

Agentic harness skeleton for aggregating and making accessible official public announcements from Innlandet (starting with Statsforvalteren i Innlandet RSS).

## What this does

One end-to-end path:

1. **Fetch** the official RSS feed.
2. **Parse & filter** items relevant to citizens (hearings, plans, roads, environment, education, housing, etc.).
3. **Produce** a structured digest (JSON + Markdown) with plain-language summaries, links, and dates.

Output correctness can be checked by verifying presence of required fields, valid URLs, non-empty summaries, and that relevant items contain expected local keywords.

## Requirements

- Python 3.9+
- `requests`

```bash
pip install -r requirements.txt
```

## Run (autonomous path)

```bash
python scripts/run_digest.py
```

This runs all stages without further human input and writes:

- `output/digest.json` (machine-checkable)
- `output/digest.md` (human-readable)

## Context

See `context/` for the system instructions and relevance criteria the full agentic version will use.

## Notes

This is a walking skeleton (Compulsory 2). The full system will replace the rule-based summary stage with an LLM agent stage, add more sources (NRK Innlandet, fylkeskommune), English translation option, evaluation harness, and safe-operation controls.
