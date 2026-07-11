---
name: show-applied-jobs
description: List all active candidaturas from data/jobs.db (SQLite). No file-based reading needed.
---

# Skill: show-applied-jobs

# Purpose

Display all active candidaturas reading from the SQLite database (`data/jobs.db`). Uses `scripts/db.py` as the data access layer.

**Principle**: DB is the source of truth. Engram and files are never used as primary data source.

---

# Process

1. **Query the database** using `scripts/db.py`:
   ```python
   from scripts.db import get_all_applications, get_status_summary
   
   # Todas las candidaturas
   apps = get_all_applications()
   
   # O filtradas por estado
   hot = get_all_applications(status_filter="hot")
   in_progress = get_all_applications(status_filter="in_progress")
   limbo = get_all_applications(status_filter="limbo")
   descartado = get_all_applications(status_filter="descartado")
   
   # Resumen
   summary = get_status_summary()
   ```

2. **Classify by status** and group:
   - 🟢 **Hot** — status "hot"
   - 🟡 **In progress** — status "in_progress"
   - ⚪ **En el limbo** — status "limbo"
   - 🔴 **Descartado** — status "descartado"

3. **Present the results** with company name, role, source platform, and latest event.

4. **If no applications found**, respond:
   "No hay candidaturas registradas. Ejecuta `/apply <empresa>` para añadir la primera."

---

# Rules

- **Never use Engram** as data source.
- **Never read companies/ directory** for listing purposes (only for NOTES.md or detailed views).
- Display in Spanish since the user communicates in Spanish.
- Group by status, ordered by priority: Hot → In progress → En el limbo → Descartado.
- Show 🟢/🟡/⚪/🔴 emoji before each company name.
- Show the latest event if available.

---

# Output format

```markdown
## 📋 Mis candidaturas

### 🟢 Hot
| # | Empresa | Rol | Origen | Prioridad | Último evento |
|---|---|---|---|---|---|
| 1 | Veriff | Senior BE — Verification Platform | LinkedIn | 93 | Stage 2 ✅ |

### 🟡 In progress
| # | Empresa | Rol | Origen | Prioridad | Último evento |
|---|---|---|---|---|---|
| 1 | Enveritas | Backend SWE — Python/Postgres | Greenhouse | 95 | applied |

### ⚪ En el limbo
*(vacío)*

### 🔴 Descartado
*(vacío)*

---
**Total activas**: X | **Descartadas**: Y
```

