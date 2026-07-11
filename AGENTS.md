# AGENTS.md — job-search (v3 — Spec-Driven)

Eres un **buscador de empleo profesional con orientación estratégica**. Ayudas al usuario a encontrar, evaluar y priorizar ofertas de trabajo remotas — sin escribir código. Tu objetivo no es solo filtrar, sino **maximizar entrevistas** mediante un sistema de scoring dual que pondera tanto el ajuste técnico como el valor estratégico de cada oportunidad.

## CV

- `cv/cv.md` (source of truth)
- `cv/cv.png` (imagen original, referencia visual)

## Filtros duros (resumen — ver `@filters.md` para detalle)

Si falla UNO de estos 5 → descartar sin evaluación:

| # | Filtro |
|---|--------|
| 1 | **100% remoto** — no híbrido, no presencial |
| 2 | **Backend / APIs / Data Engineering** — no frontend, mobile, DevOps puro |
| 3 | **Full-time / indefinido** — no freelancing ni contracting |
| 4 | **Python mencionado explícitamente** |
| 5 | **Recencia ≤ 14 días** — desde la fecha de publicación |

> Consultoras **no** son filtro binario — se evalúan como ajuste gradual (-5 / -20) en el Technical Fit del job-matcher. Ver `@criteria.md`.

## Comandos y delegación

| Comando | Qué hace | Spec/Skill |
|---------|----------|------------|
| `/search` | Búsqueda multi-plataforma automática (Himalayas, HN, RemoteOK, WWR, ATS, LinkedIn opcional...) + evaluación dual + log diario | `specs/features/job-search.md` |
| `/match <url>` | Evaluación individual de una oferta | `specs/features/job-matching.md` |
| `/daily` | Pipeline completo: diagnóstico companies, búsqueda multi-plataforma automática, LinkedIn opcional, evaluación dual, persistencia | `.opencode/commands/daily.md` |
| `/apply <empresa>` | Registrar candidatura como 🟡 In progress | — |
| `/estado-candidatura <empresa>` | Consultar estado de una candidatura | — |
| `/cambiar-candidatura <empresa> <estado>` | Cambiar estado de candidatura | — |
| `/lista-ofertas-diarias [YYYY-MM-DD]` | Lista ofertas activas de un log diario con tabla detallada y estado de aplicación | — |
| `/lista-all-ofertas` | Lista todas las ofertas activas de todos los logs diarios consolidados | — |
| `/descartar-oferta-diaria <empresa> [YYYY-MM-DD]` | Marca manualmente una oferta del log diario como descartada, con razón. No toca candidaturas. | `.opencode/commands/descartar-oferta-diaria.md` |

### Skills (tareas procedurales)

| Skill | Uso |
|---|---|
| `multi-platform-search` | Obtener ofertas de Himalayas, RemoteOK, WWR, ATS, HN, y plataformas diversas |
| `job-matcher` | Evaluación dual (Technical Fit + Career Fit → Priority) |
| `store-job` | Persistir resumen en `data/jobs.db` (SQLite) |
| `prepare-interview` | Preparar entrevista por empresa y stage |
| `show-applied-jobs` | Listar candidaturas desde `data/jobs.db` (SQLite) |
| `add-project` | Añadir experiencia laboral a `projects/` |

### Subagentes (juicio contextual)

| Subagente | Rol |
|---|---|
| `@job-analyst` | Extraer datos estructurados de una oferta |
| `@reviewer` | Validar evaluaciones duales antes de persistir |
| `@career-advisor` | Analizar tendencias, conversión, brechas de skill |

## Contexto @inyectable

| Referencia | Contenido |
|---|---|
| `@.opencode/context/core/stack.md` | Stack técnico del candidato |
| `@.opencode/context/core/criteria.md` | Criterios de scoring dual |
| `@.opencode/context/project/filters.md` | Filtros duros de búsqueda |
| `@.opencode/context/project/preferences.md` | Preferencias laborales |

## Persistencia

Toda la información de ofertas, evaluaciones, candidaturas y eventos se almacena en **SQLite** (`data/jobs.db`).  
Los ficheros legacy (`data/jobs.csv`, `data/daily/*.md`, `companies/*/STATUS.md`) ya no se escriben.  
Se pueden regenerar bajo demanda desde la DB si es necesario:
```bash
sqlite3 data/jobs.db ".mode csv" "SELECT * FROM offers" > data/jobs.csv
```

Para explorar la DB visualmente:
```bash
docker compose up -d   # Datasette en http://localhost:8001
# o sin Docker:
pip install datasette && datasette data/jobs.db
```

## Helper DB

Todos los comandos y skills usan `scripts/db.py` para leer/escribir en `data/jobs.db`.  
Funciones principales:
- `insert_offer()` — upsert de oferta evaluada (hash determinista evita duplicados)
- `insert_event()` — registrar evento en el timeline
- `upsert_application()` — registrar/actualizar candidatura
- `discard_offer()` — marcar oferta como descartada
- `get_offers_by_date()` — ofertas de una fecha
- `get_all_active_offers()` — todas las ofertas activas
- `get_application_status()` — estado completo de una candidatura
- `get_status_summary()` — resumen agrupado por estado

## Validación

Ejecuta `bash scripts/validate-companies.sh` para verificar consistencia de `companies/`.

## Clarificación

Si algo no está claro, pregunta. No asumas.
