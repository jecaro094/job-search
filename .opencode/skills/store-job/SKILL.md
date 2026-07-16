---
name: store-job
description: Save the job-matcher evaluation summary to a CSV file for tracking.
---

# Purpose

Append the result of a `job-matcher` evaluation to a persistent CSV file at `data/jobs.csv`.

The CSV serves as a lightweight tracker of all evaluated offers, their scores, and the verdict.

---

# Tasks

When the user asks to save or store an evaluation result, or after completing a `job-matcher` evaluation:

1. Read the existing CSV at `data/jobs.csv` (if it exists) to check headers.
2. Append a new row with the following columns:

```
date, job_id, company, title, score, verdict, summary
```

| Column     | Description                                      |
|------------|--------------------------------------------------|
| `date`     | ISO 8601 date (YYYY-MM-DD) of the evaluation     |
| `job_id`   | LinkedIn job ID (e.g. 4426771602)                |
| `company`  | Company name                                     |
| `title`    | Job title                                        |
| `score`    | Match score as "X/10" or "N/A"                   |
| `verdict`  | Recommendation: Apply immediately / Good opportunity / Consider applying / Skip |
| `summary`  | One-line summary of the role                     |

3. If the file does not exist, create it with the header row first.
4. Escape any commas or special characters in field values properly for CSV.
5. Confirm to the user that the entry was saved.

---

# Output

Confirm with: "Saved to data/jobs.csv: [company] — [score] — [verdict]"

No additional formatting needed — the data is persisted in the CSV.
