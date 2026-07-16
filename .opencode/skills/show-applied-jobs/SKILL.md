---
name: show-applied-jobs
description: List all active candidaturas reading from companies/*/STATUS.md files.
---

# Skill: show-applied-jobs

# Purpose

Display all active candidaturas reading from `companies/*/STATUS.md` files. Uses `data/jobs.csv` as secondary source for offer info.

**Principle**: `companies/*/STATUS.md` is the source of truth for application status. `data/jobs.csv` provides additional scoring info.

---

# Process

1. **Iterate `companies/*/STATUS.md`** files and parse:
   - Status line (`🟢 Hot`, `🟡 In progress`, `⚪ Limbo`, `🔴 Descartado`)
   - Last event in Timeline
   - Company name from the directory slug
   - Source platform line if available

2. **Cross-reference with `data/jobs.csv`** (if it exists) to get Priority Score where available.

3. **Classify by status** and group:
   - 🟢 **Hot**
   - 🟡 **In progress**
   - ⚪ **En el limbo**
   - 🔴 **Descartado**

4. **Present the results** with company name, role, source platform, and latest event.

5. **If no candidaturas found**, respond:
   "No hay candidaturas registradas. Ejecuta `/apply <empresa>` para añadir la primera."

---

# Rules

- **Never read from SQLite** (la DB está deprecada).
- Display in Spanish since the user communicates in Spanish.
- Group by status, ordered by priority: Hot → In progress → En el limbo → Descartado.
- Show 🟢/🟡/⚪/🔴 emoji before each company name.
- Show the latest event if available.
- For priority scores, parse from `data/jobs.csv` by company name.

---

# Output format

```markdown
## 📋 Mis candidaturas

### 🟢 Hot
| # | Empresa | Rol | Origen | Prioridad | Último evento |
|---|---|---|---|---|---|---|
| 1 | Veriff | Senior BE — Verification Platform | LinkedIn | 93 | Stage 2 ✅ |

### 🟡 In progress
| # | Empresa | Rol | Origen | Prioridad | Último evento |
|---|---|---|---|---|---|---|
| 1 | Enveritas | Backend SWE — Python/Postgres | Greenhouse | 95 | applied |

### ⚪ En el limbo
*(vacío)*

### 🔴 Descartado
*(vacío)*

---
**Total activas**: X | **Descartadas**: Y
```
