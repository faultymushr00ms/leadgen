# Research

This folder holds per-region research files from the research arm (ChatGPT). Files are named `REGION_YYYY-MM-DD.md`.

Each fact is labeled:

- **Confirmed** — 3+ independent sources
- **Likely - keep flagged**
- **Conflict**
- **Historical only**
- **Proven incorrect**

Nothing in this folder changes zone data by itself. Changes to `data/regions/*.json` happen only through separate reviewed pull requests.

## Audits

- `DATA-AUDIT_2026-11-22.md`: a read-only check of all 427 zone records for non-factual data (wrong displayed Δ%, placeholder priors, records that contradict themselves, stale claims). Zone data is unchanged.
