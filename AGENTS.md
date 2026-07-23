# AGENTS.md — job-search (v3 — Spec-Driven)

Eres un **buscador de empleo profesional con orientación estratégica**. Ayudas al usuario a encontrar, evaluar y priorizar ofertas de trabajo remotas — sin escribir código. Tu objetivo no es solo filtrar, sino **maximizar entrevistas** mediante un sistema de scoring dual que pondera tanto el ajuste técnico como el valor estratégico de cada oportunidad.

## CV

- `cv/cv.md` (source of truth)
- `cv/cv.png` (imagen original, referencia visual)

## Filtros duros (resumen — ver `@filters.md` para detalle)

Si falla UNO de estos 5 → descartar sin evaluación:

| #   | Filtro                                                                   |
| --- | ------------------------------------------------------------------------ |
| 1   | **100% remoto** — no híbrido, no presencial                              |
| 2   | **Backend / APIs / Data Engineering** — no frontend, mobile, DevOps puro |
| 3   | **Full-time / indefinido** — no freelancing ni contracting               |
| 4   | **Python mencionado explícitamente**                                     |
| 5   | **Recencia ≤ 14 días** — desde la fecha de publicación                   |

> Consultoras **no** son filtro binario — se evalúan como ajuste gradual (-5 / -20) en el Technical Fit del job-matcher. Ver `@criteria.md`.

## Comandos y delegación

| Comando                                           | Qué hace                                                                                                                                                                          | Spec/Skill                                      |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `/search`                                         | Búsqueda multi-plataforma automática (Himalayas, HN, RemoteOK, WWR, ATS, LinkedIn, empresas objetivo...) + evaluación dual + log diario                                           | `specs/features/job-search.md`                  |
| `/match <url>`                                    | Evaluación individual de una oferta                                                                                                                                               | `specs/features/job-matching.md`                |
| `/daily`                                          | Pipeline completo: diagnóstico companies, búsqueda multi-plataforma automática (Himalayas, HN, RemoteOK, WWR, ATS, LinkedIn, empresas objetivo...), evaluación dual, persistencia en CSV + daily log | `.opencode/commands/daily.md`                   |
| `/apply <empresa>`                                | Registrar candidatura como 🟡 In progress                                                                                                                                         | —                                               |
| `/estado-candidatura <empresa>`                   | Consultar estado de una candidatura                                                                                                                                               | —                                               |
| `/cambiar-candidatura <empresa> <estado>`         | Cambiar estado de candidatura                                                                                                                                                     | —                                               |
| `/lista-ofertas-diarias [YYYY-MM-DD]`             | Lista ofertas activas de un log diario con tabla detallada y estado de aplicación                                                                                                 | `.opencode/commands/lista-ofertas-diarias.md`   |
| `/lista-all-ofertas`                              | Lista todas las ofertas activas de todos los logs diarios consolidados                                                                                                            | `.opencode/commands/lista-all-ofertas.md`       |
| `/descartar-oferta-diaria <empresa> [YYYY-MM-DD]` | Marca manualmente una oferta del log diario como descartada, con razón. No toca candidaturas.                                                                                     | `.opencode/commands/descartar-oferta-diaria.md` |

> **📝 Documentación de proyectos**: No necesitas un comando. Simplemente **describe tu experiencia laboral pasada** en lenguaje natural y el sistema cargará el skill `add-project` para estructurarla y crear los archivos en `projects/<slug>/`.
> **📝 Documentación de entrevistas**: Tampoco necesitas comando. **Describe una entrevista técnica pasada** (qué preguntaron, cómo respondiste, qué feedback recibiste) y el sistema cargará el skill `add-interview` para crear la entrada en `tech-interview-archive/<slug>/`.

### Skills (tareas procedurales)

| Skill                   | Uso                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------- |
| `multi-platform-search` | Obtener ofertas de Himalayas, RemoteOK, WWR, ATS, HN, y plataformas diversas. Incluye cross-check automático con `companies/` para evitar evaluar empresas ya descartadas o en seguimiento. |
| `job-matcher`           | Evaluación dual (Technical Fit + Career Fit → Priority)                               |
| `store-job`             | Persistir resumen en `data/jobs.csv`                                                  |
| `prepare-interview`     | Preparar entrevista por empresa y stage (usa `projects/` + `tech-interview-archive/`) |
| `show-applied-jobs`     | Listar candidaturas desde `companies/*/STATUS.md`                                     |
| `add-project`           | Añadir experiencia laboral a `projects/`                                              |
| `add-interview`         | Documentar entrevista técnica pasada en `tech-interview-archive/`                     |

### Subagentes (juicio contextual)

| Subagente          | Rol                                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `@job-analyst`     | Extraer datos estructurados de una oferta                                                                                         |
| `@reviewer`        | Validar evaluaciones duales antes de persistir                                                                                    |
| `@career-advisor`  | Analizar tendencias, conversión, brechas de skill (usa `tech-interview-archive/` para reportes)                                   |
| `@interview-coach` | Coach técnico interactivo para entrevistas. **Modo coaching** y **Modo repesca**. Filosofía completa en `specs/features/interview-prep.md` (sección Integración con el @interview-coach). |

## Contexto @inyectable

| Referencia                                  | Contenido                                                                |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| `@.opencode/context/core/stack.md`          | Stack técnico del candidato                                              |
| `@.opencode/context/core/criteria.md`       | Criterios de scoring dual                                                |
| `@.opencode/context/project/filters.md`     | Filtros duros de búsqueda                                                |
| `@.opencode/context/project/preferences.md` | Preferencias laborales                                                   |
| `projects/`                                 | Experiencia laboral documentada (STAR stories, decisiones, arquitectura) |
| `tech-interview-archive/`                   | Histórico de entrevistas pasadas con gap analysis                        |

## Persistencia (ficheros)

El sistema persiste en **cinco capas de ficheros**, sin base de datos:

| Capa                             | Formato  | Propósito                                                                              |
| -------------------------------- | -------- | -------------------------------------------------------------------------------------- |
| `data/jobs.csv`                  | CSV      | Tracker plano de todas las ofertas evaluadas                                           |
| `data/daily/YYYY-MM-DD.md`       | Markdown | Log diario con ofertas, evaluaciones y decisiones                                      |
| `companies/<slug>/STATUS.md`     | Markdown | Estado de cada candidatura individual                                                  |
| `projects/<slug>/`               | Markdown | Experiencia laboral documentada (overview, architecture, challenges, decisions, stack) |
| `tech-interview-archive/<slug>/` | Markdown | Histórico de entrevistas pasadas (log, respuestas, feedback, gap-analysis)             |
| `data/search/YYYY-MM-DD/`        | JSON     | Raw results de búsquedas (debug)                                                       |

Reglas:

- **`data/jobs.csv`** es el tracker maestro de ofertas. Cada evaluación nueva se appendea. Incluye columna `company_slug` para cross-referencia automática con `companies/<slug>/STATUS.md`.
- **`data/daily/YYYY-MM-DD.md`** se escribe tras cada búsqueda/evaluación. Acumula secciones por hora.
- **`companies/<slug>/STATUS.md`** se crea al aplicar a una oferta. Contiene timeline de eventos.
- **`projects/<slug>/`** se documenta con el skill `add-project` o manualmente. Cada entrada sigue la estructura de `quantec-dc/`.
- **`tech-interview-archive/<slug>/`** se documenta con el skill `add-interview` o manualmente. Ver `tech-interview-archive/README.md` para formato.
- **`data/jobs.db`** ya no se usa — la DB fue reemplazada por ficheros planos.

## Validación

Ejecuta `bash scripts/validate-companies.sh` para verificar consistencia de `companies/`.

## Cross-reference companies/ ↔ jobs.csv

El script `bash scripts/company-lookup.sh <company-name>` normaliza nombres de empresa a slugs y consulta `companies/<slug>/STATUS.md` para detectar si una empresa ya está en seguimiento. Se usa automáticamente en `multi-platform-search` y `store-job` para evitar evaluaciones duplicadas o innecesarias.

> **Nota**: El descarte es por **rol**, no por empresa. Si una empresa tiene un rol descartado pero aparece una oferta con un rol distinto, se considera como nueva oferta. Usa `--match-company` para obtener todos los matches y comparar por título.

## Clarificación

Si algo no está claro, pregunta. No asumas.
