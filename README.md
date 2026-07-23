# job-search

Automated job search agent for remote backend/data/API engineering roles in Spain.

## Overview

This project uses [opencode](https://opencode.ai) with AI agent workflows to proactively search, evaluate, and track remote job listings across multiple platforms. It runs as a CLI-driven assistant that follows dual scoring criteria (Technical Fit + Career Fit → Priority).

## Features

- **Proactive daily search** — searches Himalayas, Hacker News, LinkedIn, RemoteOK, We Work Remotely, ATS platforms (Greenhouse, Lever, Ashby, Workable), and target companies
- **Auto-evaluation** — scores listings against CV using the `job-matcher` skill (dual scoring: Technical Fit + Career Fit → Priority)
- **Strict filtering** — 5 hard filters: 100% remote, backend/API role, full-time, Python required, recency ≤14d. Consultancy type is scored gradually (no longer a binary cut)
- **Persistent tracking** — all evaluations saved to `data/jobs.csv` + daily logs in `data/daily/YYYY-MM-DD.md`
- **Application workflow** — per-company tracking via `companies/<slug>/STATUS.md` and Q&A via `companies/<slug>/NOTES.md`
- **Engram memory** — remembers past decisions, rejected companies, and application status across sessions
- **Cross-reference** — `companies/` ↔ `jobs.csv` via `scripts/company-lookup.sh` to avoid duplicate evaluations

## Configuration

- `AGENTS.md` — agent instructions and workflow rules
- `opencode.json` — opencode config
- `.opencode/skills/` — custom skills (`multi-platform-search`, `job-matcher`, `store-job`, `prepare-interview`, `show-applied-jobs`, `add-project`, `add-interview`)
- `.opencode/context/` — criteria, filters, stack, preferences
- `data/jobs.csv` — evaluation results log (76 entries as of 2026-07-23)

## Skills

| Skill | Description |
|---|---|
| `multi-platform-search` | Searches Himalayas, LinkedIn, RemoteOK, WWR, HN, ATS, and target companies. Includes cross-check with `companies/` to avoid re-evaluating |
| `job-matcher` | Evaluates job fit against CV with dual scoring (Technical Fit + Career Fit → Priority) |
| `store-job` | Persists evaluation summaries to `data/jobs.csv` |
| `prepare-interview` | Prepares for a specific company's next interview stage |
| `show-applied-jobs` | Lists active candidaturas from `companies/*/STATUS.md` |
| `add-project` | Documents a past work experience into `projects/` |
| `add-interview` | Documents a past technical interview into `tech-interview-archive/` |

## Subagentes

| Subagente | Rol |
|---|---|
| `@job-analyst` | Extrae datos estructurados de una oferta de empleo |
| `@reviewer` | Valida evaluaciones duales antes de persistirlas |
| `@career-advisor` | Analiza tendencias del mercado y rendimiento de candidaturas |
| `@interview-coach` | Coach técnico interactivo: system design, live coding, SQL, patrones distribuidos. Modo coaching y Modo repesca |

---

## Usage

Start a session:
```bash
opencode
```

Then interact with the agent using natural language. Below are examples for each capability.

### Comandos de búsqueda y evaluación

```bash
# Búsqueda multi-plataforma (Himalayas, HN, RemoteOK, WWR, ATS, LinkedIn...)
/search

# Evaluar una oferta individual por URL
/match https://example.com/backend-job

# Pipeline completo: diagnóstico + búsqueda multi-plataforma + evaluación + persistencia
/daily
```

### Comandos de candidaturas

```bash
# Registrar que has aplicado a una empresa
/apply octopus-energy-group

# Consultar estado de una candidatura
/estado-candidatura octopus-energy-group

# Cambiar el estado de una candidatura (🟢 Hot / 🟡 In progress / 🔴 Discarded / ⚪ Limbo)
/cambiar-candidatura octopus-energy-group hot

# Listar todas las ofertas activas de un log diario concreto
/lista-ofertas-diarias 2026-07-23

# Listar todas las ofertas activas de todos los logs consolidados
/lista-all-ofertas

# Descartar manualmente una oferta del log diario (sin tocar candidaturas)
/descartar-oferta-diaria veriff 2026-07-13
```

### Subagentes

```bash
# Analizar una oferta en profundidad
@job-analyst analiza esta oferta: https://example.com/backend-job

# Revisar una evaluación antes de guardarla
@reviewer valida esta evaluación

# Consejo estratégico semanal
@career-advisor haz el informe semanal

# Entrenamiento técnico para entrevistas
@interview-coach ponme un ejercicio de system design
@interview-coach quiero practicar live coding Python
@interview-coach hazme preguntas de Kafka
@interview-coach tengo entrevista en Veriff, prepárame
```

### Skills (vía el orquestador)

```bash
# Preparar la siguiente entrevista de una empresa
skill: prepare-interview for veriff

# Documentar una experiencia laboral en projects/
Quiero documentar mi proyecto de Mapfre, usé Django, Kafka y Celery

# Documentar una entrevista técnica pasada
Tuve una entrevista en Veriff donde me preguntaron sobre Kafka y system design

# Listar candidaturas activas
¿Qué candidaturas tengo activas?

# Ver estado de todas las empresas en proceso
¿Cómo voy con las candidaturas?
```

### Ejemplo de sesión completa

```text
Usuario:
  /daily

Agente:
  Diagnostica candidaturas activas, ejecuta búsqueda multi-plataforma,
  aplica 5 filtros duros, evalúa ofertas con scoring dual
  (Technical Fit + Career Fit → Priority), persiste en data/jobs.csv
  y genera log en data/daily/YYYY-MM-DD.md.

Usuario:
  /apply octopus-energy-group

Agente:
  Crea companies/octopus-energy-group/STATUS.md, actualiza jobs.csv,
  guarda en Engram, pregunta si quiere añadir Q&A en NOTES.md.

Usuario:
  @interview-coach ponme un ejercicio de system design

@interview-coach:
  🎯 Ejercicio: Diseña un sistema de rate limiting para una API pública
  ...
```

> **Tip:** Los subagentes se invocan con `@nombre` y los comandos con `/comando`.  
> El orquestador decide automáticamente qué skill o subagente delegar según la tarea.
