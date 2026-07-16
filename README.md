# job-search

Automated job search agent for remote backend/data/API engineering roles in Spain.

## Overview

This project uses [opencode](https://opencode.ai) with AI agent workflows to proactively search, evaluate, and track LinkedIn job listings. It runs as a CLI-driven assistant that follows strict filtering criteria.

## Features

- **Proactive daily search** — searches LinkedIn for new remote backend/data/API jobs in Spain each session
- **Auto-evaluation** — scores listings against CV (`cv/cv.png`) using the `job-matcher` skill
- **Strict filtering** — remote-only, product companies (no consultancies), full-time, posted within last week
- **Persistent tracking** — all evaluations saved to `data/jobs.csv`
- **Engram memory** — remembers past decisions, rejected companies, and application status across sessions

## Configuration

- `AGENTS.md` — agent instructions and workflow rules
- `opencode.json` — opencode config (Composio MCP integration)
- `.opencode/skills/` — custom skills (`multi-platform-search`, `job-matcher`, `store-job`)
- `data/jobs.csv` — evaluation results log (48 entries as of 2026-07-06)

## Skills

| Skill | Description |
|---|---|
| `multi-platform-search` | Searches Himalayas, RemoteOK, WWR, HN, ATS platforms |
| `job-matcher` | Evaluates job fit against CV and filters |
| `store-job` | Persists evaluation summaries to CSV |
| `prepare-interview` | Prepares for a specific company's next interview stage |
| `show-applied-jobs` | Lists active candidaturas from `companies/*/STATUS.md` |
| `add-project` | Documents a past work experience into `projects/` |

## Subagentes

| Subagente | Rol |
|---|---|
| `@job-analyst` | Extrae datos estructurados de una oferta de empleo |
| `@reviewer` | Valida evaluaciones duales antes de persistirlas |
| `@career-advisor` | Analiza tendencias del mercado y rendimiento de candidaturas |
| `@interview-coach` | Coach técnico: system design, live coding, SQL, patrones distribuidos |

---

## Usage

Start a session:
```bash
opencode
```

Then interact with the agent using natural language. Below are examples for each capability.

### Comandos de búsqueda y evaluación

```bash
# Búsqueda multi-plataforma automática (Himalayas, HN, RemoteOK, WWR, ATS, LinkedIn...)
/search

# Evaluar una oferta individual por URL
/match https://remotive.com/remote-jobs/backend/example

# Pipeline completo: diagnóstico + búsqueda + evaluación + persistencia
/daily
```

### Comandos de candidaturas

```bash
# Registrar que has aplicado a una empresa
/apply veriff

# Consultar estado de una candidatura
/estado-candidatura veriff

# Cambiar el estado de una candidatura (e.g. cuando pasas de fase)
/cambiar-candidatura veriff hot

# Listar todas las ofertas activas de un log diario concreto
/lista-ofertas-diarias 2026-07-13

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
  Busca ofertas en 6 plataformas, evalúa cada una contra tu CV,
  aplica filtros duros (remoto, backend, Python, full-time, recencia),
  calcula dual scoring (Technical Fit + Career Fit),
  persiste en data/jobs.csv y genera log en data/daily/2026-07-13.md.

Usuario:
  @interview-coach ponme un ejercicio de system design

@interview-coach:
  🎯 Ejercicio: Diseña un sistema de rate limiting para una API pública
  ...
```

> **Tip:** Los subagentes se invocan con `@nombre` y los comandos con `/comando`.  
> El orquestador decide automáticamente qué skill o subagente delegar según la tarea.
