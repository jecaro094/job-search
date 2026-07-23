---
name: store-job
description: Save the job-matcher evaluation summary to a CSV file for tracking.
---

# Purpose

Persist the result of a `job-matcher` evaluation to `data/jobs.csv` usando el script `scripts/append-job.py` que maneja **deduplicación automática** (upsert).

Si ya existe una fila con la misma `company_slug` + `title`, la **actualiza** en vez de duplicarla. Si no existe, la **appendea**.

---

# Tasks

When the user asks to save or store an evaluation result, or after completing a `job-matcher` evaluation:

1. Generate the `company_slug` by calling:
   ```
   bash scripts/company-lookup.sh "<company-name>"
   ```
   This returns JSON with the slug. Use the `slug` field from the response.
   - If the slug is empty or not found, generate it manually: lowercase → eliminar paréntesis → spaces a hyphens → collapse.

2. Build the field=value arguments y llama al script:
   ```bash
   python3 scripts/append-job.py \
     "date=$(date +%Y-%m-%d)" \
     "company=<company-name>" \
     "company_slug=<slug>" \
     "title=<job-title>" \
     "url=<url>" \
     "technical_fit=<score>" \
     "career_fit=<score>" \
     "priority_score=<score>" \
     "green_flags=<flags-summary>" \
     "red_flags=<flags-summary>" \
     "difficulty=<Easy|Medium|Hard>" \
     "verdict=<verdict>" \
     "summary=<one-line-summary>" \
     "source_platforms=<platforms>" \
     "applied=" \
     "status="
   ```

3. El script devuelve `"appended"` o `"upserted"`. Confirma al usuario:
   ```
   Saved to data/jobs.csv: [company] ([company_slug]) — Priority [score] — [verdict] ([action])
   ```
   donde `[action]` es "añadida" si fue appended, o "actualizada" si fue upserted.

### Reglas para los campos

| Campo | Descripción |
|-------|-------------|
| `date` | ISO 8601 date (YYYY-MM-DD) de la evaluación |
| `company` | Company name (human-readable) |
| `company_slug` | Normalized slug (e.g. `bmat-music-innovations`) |
| `title` | Job title |
| `url` | Full URL to the job posting |
| `technical_fit` | Technical Fit score (0-100) |
| `career_fit` | Career Fit score (0-100) |
| `priority_score` | Priority Score (0-100) |
| `green_flags` | Green flags summary, e.g. "+22: small-team, funding, ownership" |
| `red_flags` | Red flags summary, e.g. "-4: hidden-salary" |
| `difficulty` | Easy / Medium / Hard |
| `verdict` | Apply immediately / Apply / Consider applying / Skip |
| `summary` | One-line summary of the role (max 200 chars) |
| `source_platforms` | Platforms where found, separated by comma (e.g. "LinkedIn,Himalayas") |
| `applied` | Fecha de aplicación (YYYY-MM-DD) o vacío |
| `status` | `discarded` o vacío |

**Nota**: El script `append-job.py` escapa automáticamente comillas y comas. No hace falta escapado manual.

---

# Output

Confirm with: "Saved to data/jobs.csv: [company] ([company_slug]) — Priority [score] — [verdict] (añadida/actualizada)"
