---
name: store-job
description: Save the job-matcher evaluation summary to SQLite (jobs.db) for querying and tracking.
---

# Purpose

Persist the result of a `job-matcher` evaluation to the SQLite database at `data/jobs.db`.

The DB serves as the structured source of truth for all evaluated offers, their scores, green/red flags, verdict, and lifecycle events.

---

# Database Schema

See `db/schema.sql` for full DDL. The relevant table is `offers`:

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Deterministic hash(company+role+url) |
| `company` | TEXT | Company name |
| `company_slug` | TEXT | Normalized slug |
| `role` | TEXT | Job title |
| `url` | TEXT | URL to the job posting |
| `tech_fit` | INTEGER | Technical Fit score (0–100) |
| `career_fit` | INTEGER | Career Fit score (0–100) |
| `priority` | INTEGER | Priority Score (0–100) |
| `green_flags` | INTEGER | Green flags points total |
| `red_flags` | INTEGER | Red flags points total |
| `difficulty` | TEXT | Easy / Medium / Hard |
| `verdict` | TEXT | Apply immediately / Apply / Consider / Skip |
| `summary` | TEXT | One-line summary |
| `source_platforms` | TEXT | Platforms where found |
| `status` | TEXT | active / applied / discarded / expired / closed |
| `discovery_date` | DATE | Date the offer was found |

---

# Process

When the user asks to save an evaluation, or after completing a `job-matcher` evaluation:

1. **Prepare the data** with the same fields as the evaluation output.
2. **Call `scripts/db.py`** using:
   ```python
   from scripts.db import insert_offer
   offer_id = insert_offer(
       company=..., role=..., url=..., tech_fit=..., career_fit=...,
       priority=..., green_flags=..., red_flags=..., difficulty=...,
       verdict=..., summary=..., source_platforms=..., platform=...,
       discovery_date=...
   )
   ```
3. **Deduplication is automatic**: `insert_offer` uses `INSERT OR REPLACE` with a deterministic hash ID. Same company+role+url → same row, updated with latest scores.
4. **Record an event** for the evaluation timeline:
   ```python
   from scripts.db import insert_event
   insert_event(offer_id, "evaluated", f"Priority {priority}/100 — {verdict}")
   ```
5. **Confirm** to the user.

## CSV export (optional)

The CSV at `data/jobs.csv` is no longer the source of truth. It can be regenerated at any time:
```bash
sqlite3 data/jobs.db ".mode csv" "SELECT * FROM offers" > data/jobs.csv
```

---

# Output

Confirm with: "✅ Saved to jobs.db: [company] — Priority: [score]/100 — [verdict]"

If duplicate (same hash): "ℹ️ [Company] already tracked. Scores updated."
