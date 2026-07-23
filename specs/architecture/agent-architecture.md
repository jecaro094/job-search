# Arquitectura del agente job-search (v5 — file-based)

> **Decisión de arquitectura (2026-07-11)**: El sistema abandonó SQLite (`data/jobs.db`) como fuente de verdad y opera exclusivamente sobre **ficheros planos** (CSV + Markdown). Motivos: (1) trazabilidad vía git — cada cambio es un diff visible, (2) cero infraestructura — no requiere Python runtime para consultas básicas, (3) inspección directa — cualquier fichero se lee con `cat` o `grep` sin herramientas adicionales. Los artefactos de la migración a SQLite (`data/jobs.db`, `scripts/db.py`, `specs/architecture/persistence-data.md`) se mantienen como histórico pero **no se utilizan** en el flujo activo. Ver `AGENTS.md` → *Persistencia (ficheros)* para la documentación operativa.

## 1. Diagrama de componentes

```
┌──────────────────────────────────────────────────────────────────┐
│                        ORQUESTADOR                                │
│                   (agente principal)                              │
│  • Interpreta comandos y lenguaje natural                         │
│  • Decide cuándo delegar vs. ejecutar directo                     │
│  • Mantiene coherencia entre ficheros y memoria                   │
│  • Actualiza tasks/current.md                                     │
│  • Orquesta pipelines multi-paso (buscar → evaluar → persistir)   │
└──────┬────────────┬──────────────┬────────────────┬──────────────┘
       │            │              │                │
  ┌────▼────┐  ┌────▼────┐   ┌────▼─────┐    ┌────▼─────┐
  │ SKILLS  │  │SUBAG.   │   │ FICHEROS  │    │CONTEXTO  │
  │(carga   │  │(delega  │   │(source    │    │@inyectable│
  │ bajo    │  │ juicio) │   │ of truth) │    │          │
  │ demanda)│  │         │   │           │    │          │
  └────┬────┘  └────┬────┘   └───────────┘    └────┬──────┘
       │            │                              │
  ┌────▼────────────┐   ┌────────────────────┐     │
  │ SKILLS disponibles  │   SUBAGENTES          │    │
   │   (multi-platform)  │   │• @job-analyst      │    │
  │• multi-platform    │   │• @career-advisor   │    │
  │  (Himalayas/HN/WWR)│   └────────────────────┘    │
  │• job-matcher*      │                             │
  │• store-job         │   ┌────────────────────┐     │
  │• prepare-interview │   │ COMMANDS            │    │
   │• show-applied-jobs │   │• /search            │    │
   │• add-project       │   │• /match <url>       │    │
   └────────────────────┘   │• /daily             │    │
                            │• /apply             │    │
    *dual scoring           │• /cambiar-candidatura│    │
                            │• /company           │    │
                            │• /lista-ofertas-    │    │
                            │   diarias           │    │
                            │• /lista-all-ofertas │    │
                            └────────────────────┘    │
                                         ┌───────────┴──────────┐
                                         │ CONTEXTO @inyectable  │
                                         │• @filters.md          │
                                         │• @criteria.md         │
                                         │• @stack.md            │
                                         │• @preferences.md      │
                                         └──────────────────────┘
```

## 2. Responsabilidades del orquestador

| Responsabilidad | Qué hace |
|---|---|
| **Parseo de entrada** | Interpreta comandos (`/search`, `/daily`, `/match`, `/apply`, `/estado-candidatura`, `/cambiar-candidatura`, `/lista-ofertas-diarias`, `/lista-all-ofertas`, `/descartar-oferta-diaria`) y lenguaje natural |
| **Enrutamiento** | Decide qué skill cargar o a qué subagente delegar según tabla de delegación |
| **Flujo de trabajo** | Orquesta pipelines multi-paso (buscar → pre-filtrar → evaluar → validar → persistir) |
| **Validación** | Verifica que los ficheros queden consistentes tras cada operación |
| **Memoria** | Guarda en Engram tras cada interacción relevante (decisiones, aplicaciones, descartes) |
| **Tracking** | Mantiene `tasks/current.md` visible |

### Tabla de delegación

| Tarea | Subagente / Skill |
|---|---|
| Análisis profundo de ofertas | @job-analyst |
| Búsqueda proactiva (multi-plataforma) | skill `multi-platform-search` + skill `job-matcher` |
| Búsqueda multi-plataforma (sin MCP) | skill `multi-platform-search` + skill `job-matcher` |
| Evaluación técnica | skill `job-matcher` |
| Revisión de evaluaciones | @reviewer |
| Preparación de entrevistas (por empresa) | skill `prepare-interview` |
| Entrenamiento técnico genérico | @interview-coach |
| Documentación de proyectos laborales | skill `add-project` |
| Documentación de entrevistas técnicas | skill `add-interview` |
| Análisis de tendencias / conversión | @career-advisor |

## 3. ¿Skill o subagente? Regla de decisión

```
┌──────────────────────────────────────────────┐
│ ¿La tarea sigue un pipeline fijo/repetitivo?  │
├───────────┬──────────────────────────────────┤
│    SÍ     │           NO                      │
│  → SKILL  │       → SUBAGENTE                 │
│           │                                   │
│ Ejemplos: │ Ejemplos:                         │
│ • multi-platform-search (mismo proceso)       │
│ • job-matcher (evaluación estructurada)       │
│ • store-job (persistir siempre igual)         │
│ • prepare-interview (checklist fijo)          │
│ • show-applied-jobs (listado directo)         │
│ • add-project (documentación laboral)         │
└───────────┴───────────────────────────────────┘
```

### ¿Por qué job-matcher es skill y no subagente?
Porque su proceso es **mayoritariamente determinista**: recibe oferta → aplica reglas de scoring dual → devuelve priority score. Sigue un pipeline fijo (pre-filtros → Technical Fit → Career Fit → Green/Red Flags → Priority).

### ¿Por qué @job-analyst, @reviewer y @career-advisor son subagentes?
Porque requieren **juicio contextual**: el analyst interpreta una oferta ambigua y extrae lo relevante; el reviewer decide si una evaluación es sólida o tiene sesgos; el career-advisor analiza tendencias agregadas y recomienda estrategia.

### Scoring dual (v4)

El sistema usa **3 scores** con fórmula:

- **Technical Fit** (0-100): mide capacidad técnica contra el stack del candidato (6 factores ponderados)
  - Python (30%), APIs/FastAPI/Django (20%), SQL/Databases (15%), Kafka/messaging (10%), Docker/AWS (10%), Seniority match (15%)
  - + Ajustes por fecha publicación (+0 a -15), tipo empresa (+15 a -20), plataforma (+5 a +10)

- **Career Fit** (0-100): mide interés estratégico
  - Salary (20%), Product quality (15%), Company size (10%), Domain (10%), Eng culture (15%), Growth (10%), Timezone (10%), Modern stack (10%)

- **Priority Score** (0-100): síntesis ponderada

```
Priority = (Tech × 0.5) + (Career × 0.5) + GreenFlags - RedFlags - DifficultyPenalty
```

| Componente | Descripción |
|---|---|
| Green Flags | Bonos por cultura, stack, misión (ej: +5 engineering-driven, +3 small team) |
| Red Flags | Penalizaciones por señales negativas (ej: -4 salary hidden) |
| Difficulty Penalty | -3 ajuste por dificultad del proceso (bonus si el proceso es ligero) |

Los filtros binarios son 5 duros (remoto, rol, full-time, Python, ubicación). Fecha y tipo empresa son scoring gradual.

## 4. Ciclo de vida de una candidatura

```
Descubrimiento → Pre-filter → Evaluación Dual → Ranking → Aplicación → Progreso → Resolución
      │              │              │             │           │           │          │
      ▼              ▼              ▼             ▼           ▼           ▼          ▼
    /daily        5 cortes       job-matcher               /apply      /cambiar-candidatura
    /search       binarios      (dual score)             (STATUS.md)   (STATUS.md)   🔴❌⚪
    /match <url>                                          + NOTES.md  + Timeline
```

| Fase | Acción | Comando | Persistencia |
|---|---|---|---|---|---|
| **Descubrimiento** | Buscar ofertas en multi-plataforma + LinkedIn (optativo) | `/daily`, `/search` | `data/search/YYYY-MM-DD/HH-MM-{channel}.json` (raw, opcional) |
| **Pre-filter** | 5 cortes binarios (remoto, rol, full-time, Python, ubicación) | Automático | No aplica (solo en memoria) |
| **Evaluación** | Scoring dual (Tech Fit + Career Fit → Priority) | `/match <url>` | `data/jobs.csv` (append row) + `data/daily/YYYY-MM-DD.md` (log section) |
| **Ranking** | Ordenación por Priority Score | Automático | No aplica (ordenación en memoria) |
| **Aplicación** | Registrar que has aplicado + guardar respuestas | `/apply <empresa>` | `companies/<slug>/STATUS.md` (crear con timeline) + `data/jobs.csv` (actualizar estado) |
| **Progreso** | Avanzar etapas del proceso | Natural / `/cambiar-candidatura` | `companies/<slug>/STATUS.md` (actualizar timeline + estado) |
| **Resolución** | Cambiar a Hot/Descartado/Limbo | Natural / `/cambiar-candidatura` | `companies/<slug>/STATUS.md` + opcional `companies/<slug>/feedback_*.md` |

## 5. Comandos del sistema

| Comando | Función | Spec |
|---|---|---|
| `/search` | Búsqueda multi-plataforma automática (Himalayas, HN, RemoteOK, WWR, ATS) + evaluación dual + log diario | `specs/features/job-search.md` |
| `/daily` | Pipeline completo: diagnóstico companies + búsqueda multi-plataforma (Himalayas, HN, RemoteOK, WWR, ATS, LinkedIn, empresas objetivo) + evaluación dual + persistencia CSV + daily log | `.opencode/commands/daily.md` |
| `/match <url>` | Evaluación individual de una oferta con scoring dual | `specs/features/job-matching.md` |
| `/apply <empresa>` | Registrar candidatura como 🟡 In progress. Crea `companies/<slug>/STATUS.md` + pregunta por Q&A | — |
| `/estado-candidatura <empresa>` | Consultar estado de una candidatura desde `companies/<slug>/STATUS.md` | — |
| `/cambiar-candidatura <empresa> <estado>` | Cambiar estado (🟢 Hot / 🟡 In progress / 🔴 Discarded / ⚪ Limbo) | — |
| `/lista-ofertas-diarias [YYYY-MM-DD]` | Extraer y mostrar tabla de ofertas no descartadas del daily log con estado de aplicación | `.opencode/commands/lista-ofertas-diarias.md` |
| `/lista-all-ofertas` | Listar todas las ofertas activas de todos los logs diarios consolidados | `.opencode/commands/lista-all-ofertas.md` |
| `/descartar-oferta-diaria <empresa> [YYYY-MM-DD]` | Marcar oferta como descartada en el daily log con razón. No afecta candidaturas | `.opencode/commands/descartar-oferta-diaria.md` |

## 6. Canales de búsqueda y pipelines

| Canal | Cómo se obtiene | Pipeline | Rate limit |
|---|---|---|---|
| **Himalayas** | `websearch` + `webfetch` API (`himalayas.app/jobs/api/search`) | Multi-platform-search | Ilimitado |
| **Hacker News** | `webfetch` a `hnhiring.com` (agregador parseado con LLM) | Multi-platform-search | 1x/día (solo Jul) |
| **RemoteOK** | `websearch` + `webfetch` | Multi-platform-search | Ilimitado |
| **We Work Remotely** | `websearch` + `webfetch` | Multi-platform-search | Ilimitado |
| **ATS directo** | `websearch` para ofertas en Greenhouse, Ashby, Lever, Recruitee | Multi-platform-search | Ilimitado |
| **LinkedIn** | `websearch` para ofertas de LinkedIn (captura ~10-15% de ofertas indexadas) | Multi-platform-search | 2-8 queries por daily |
| **Empresas objetivo** (Step 8) | Shortlist diaria (~10 empresas remote-first + Python) + full scan semanal (~40 empresas rotadas) | Multi-platform-search | Diario/semanal |
| **Evaluación individual** | `webfetch` directo a URL | `/match <url>` + `job-matcher` | Ilimitado |

### Pipeline HN "Who is hiring"

```
1. webfetch → hnhiring.com (parsea ~400 comments del thread mensual)
2. LLM filtra ofertas que mencionan Python + backend + remote + Europe/EMEA
3. Pre-filter + job-matcher para cada oferta candidata
4. Persistencia en 3 capas de ficheros: `data/jobs.csv` + `data/daily/YYYY-MM-DD.md` + `companies/<slug>/STATUS.md`
```

### Post-search — Verificación de ejecución

Tras cada `/daily`, el orquestador debe incluir en el log diario un resumen con:

- **Canales ejecutados**: lista de canales procesados
- **Canales omitidos**: si alguno no se ejecutó, justificación
- **Total ofertas descubiertas por canal**

Esto asegura trazabilidad de lo ejecutado en cada daily.

## 7. Persistencia (ficheros planos como fuente de verdad)

El sistema persiste en **cinco capas de ficheros**, sin base de datos externa. Esta decisión es deliberada: los ficheros planos son legibles, versionables con git y no requieren infraestructura.

| Capa | Formato | Propósito | Estado |
|------|---------|-----------|--------|
| **`data/jobs.csv`** | CSV | Tracker maestro de todas las ofertas evaluadas con scores, veredicto, plataforma y estado de aplicación | ✅ Activo |
| **`data/daily/YYYY-MM-DD.md`** | Markdown | Log diario humano-legible con ofertas, evaluaciones, decisiones y métricas por búsqueda | ✅ Activo |
| **`companies/<slug>/STATUS.md`** | Markdown | Estado (🟢🟡🔴⚪) y timeline de cada candidatura individual | ✅ Activo |
| **`projects/<slug>/`** | Markdown | Experiencia laboral documentada (overview, architecture, challenges, decisions, stack) | ✅ Activo |
| **`tech-interview-archive/<slug>/`** | Markdown | Histórico de entrevistas pasadas (log, respuestas, feedback, gap-analysis) | ✅ Activo |
| `companies/<slug>/NOTES.md` | Markdown | Notas de entrevista, respuestas de formularios, Q&A | ✅ Información no estructurada |
| `companies/<slug>/feedback_*.md` | Markdown | Feedback post-entrevista por stage | ✅ Información no estructurada |
| `data/search/YYYY-MM-DD/` | JSON | Raw results por canal de búsqueda (debug) | Opcional |
| `data/jobs.db` | SQLite | Migración cancelada — *no se usa*. `data/jobs.db` fue un intento de migración a SQLite que quedó en desuso; el sistema actual opera exclusivamente sobre ficheros planos. | ❌ No usado |

### Reglas de persistencia

1. **`data/jobs.csv`** — Tracker maestro de ofertas. Cada evaluación nueva se appendea como fila. Contiene: empresa, rol, URL, Technical Fit, Career Fit, Priority Score, green/red flags, difficulty, verdict, summary, source_platforms, applied date, status. Incluye columna `company_slug` para cross-referencia con `companies/`.
2. **`data/daily/YYYY-MM-DD.md`** — Se escribe tras cada búsqueda/evaluación. Acumula secciones por hora. Contiene tabla de ofertas evaluadas, TOP oferta, y ofertas descartadas con razón.
3. **`companies/<slug>/STATUS.md`** — Se crea al aplicar a una oferta. Contiene estado actual, timeline de eventos (aplicación, entrevistas, cambios de estado), y fuente.
4. **`companies/<slug>/NOTES.md`** — Se crea opcionalmente tras aplicar. Contiene Q&A del formulario de candidatura e información adicional.
5. **Nunca escribir en `data/jobs.db`** — ese fichero es legacy de una migración abortada.

Ver `AGENTS.md` → sección *Persistencia (ficheros)* para la documentación operativa oficial.

## 8. Fuentes de verdad

| Dato | Fuente | Notas |
|---|---|---|
| Evaluaciones técnicas | `data/jobs.csv` | CSV con Technical Fit, Career Fit, Priority, flags y veredicto |
| Estado de candidatura | `companies/<slug>/STATUS.md` | Markdown con estado actual + timeline de eventos |
| Detalle de empresa | `data/daily/*.md` + `companies/<slug>/NOTES.md` | Evaluaciones completas en daily logs; notas de entrevista en companies/ |
| Respuestas de formularios | `companies/<slug>/NOTES.md` | Q&A de aplicaciones, respuestas preparadas |
| Feedback por etapa | `companies/<slug>/feedback_*.md` | Notas post-entrevista por stage |
| Logs de búsqueda | `data/daily/*.md` | Log diario con métricas por canal y decisiones |
| Resultados brutos | `data/search/YYYY-MM-DD/` (opcional) | Raw JSON por canal de búsqueda |
| CV del candidato | `cv/cv.md` | Source of truth del perfil técnico |
| Memoria entre sesiones | Engram | Solo contexto, nunca fuente primaria de datos |

## 9. Contexto @inyectable

El orquestador puede inyectar contexto en sus prompts usando referencias `@`:

| Referencia | Contenido |
|---|---|
| `@.opencode/context/core/stack.md` | Stack técnico del candidato |
| `@.opencode/context/core/criteria.md` | Criterios de scoring dual |
| `@.opencode/context/project/filters.md` | Filtros duros de búsqueda |
| `@.opencode/context/project/preferences.md` | Preferencias laborales |

Estas referencias se pasan a subagentes y skills cuando la tarea lo requiere.

## 10. Protocolo orquestador → subagente / skill

### Engram protocol — Conflict Judgment

Tras cada `mem_save`, el orquestador debe comprobar `judgment_required` en la respuesta. Si es `true`:

1. Iterar `candidates[]` y evaluar cada conflicto
2. Si **confianza ≥ 0.7** y la relación no es `supersedes`/`conflicts_with` sobre `architecture`/`policy`/`decision` → resolver silenciosamente con `mem_judge`
3. Si **confianza < 0.7** o la relación requiere decisión del usuario → preguntar al usuario de forma conversacional
4. Guardar el veredicto con `mem_judge`

### Cuándo delegar en cada subagente

| Subagente | Cuándo invocarlo | Nunca delegar si... |
|---|---|---|
| `@job-analyst` | **Siempre que llegue una URL nueva** para evaluación individual (`/match` o `/daily` con oferta individual). Extrae datos estructurados de la oferta antes de pasar a `job-matcher`. | La oferta ya está clara y estructurada desde el snippet (ej: formato ATS bien definido). |
| `@reviewer` | **Siempre antes de persistir** una evaluación con Priority ≥85 o con dudas (green/red flags borderline). Valida consistencia, sesgos, filtros. | La evaluación es rutinaria (Priority <70) o el análisis es trivial. |
| `@career-advisor` | **Semanalmente** (o cuando el usuario pida análisis de tendencias/conversión). También tras 3+ nuevas aplicaciones para revisar cartera. | Consultas puntuales sobre una sola oferta. |

### Protocolo genérico de delegación

```
1. ORQUESTADOR: Prepara contexto (URL, oferta, criterios, @context si aplica)
2. ORQUESTADOR: Envía prompt con instrucciones explícitas y formato de salida
3. SUBAGENTE: Ejecuta análisis y devuelve resultado estructurado
4. ORQUESTADOR: Valida que el resultado sea utilizable
5. ORQUESTADOR: Persiste si procede (en ficheros: append a `data/jobs.csv`, escribe `data/daily/YYYY-MM-DD.md`, crea/actualiza `companies/<slug>/STATUS.md` si aplica)
6. ORQUESTADOR: Guarda en Engram (mem_save) si es decisión relevante
7. ORQUESTADOR: Informa al usuario
```

### Flujo de evaluación con subagentes (`/match <url>` y `/daily`)

```
1. Llega URL de oferta
2. ─→ ORQUESTADOR invoca @job-analyst con la URL + @filters.md + @criteria.md
3.   ─→ @job-analyst devuelve: empresa, rol, stack, seniority, ubicación, 
        salario, fecha publicación, fit preliminar, señales de alerta
4. ─→ ORQUESTADOR pasa datos extraídos a job-matcher (skill)
5.   ─→ job-matcher devuelve: Technical Fit, Career Fit, Priority, 
        green/red flags, difficulty, skill gaps, strengths
6. ─→ ORQUESTADOR invoca @reviewer con la evaluación completa + oferta original
7.   ─→ @reviewer devuelve: Aprobado/Rechazado + razón + sugerencias
8. ─→ ORQUESTADOR persiste: appendea a `data/jobs.csv` (via `store-job`), escribe sección en `data/daily/YYYY-MM-DD.md`, y si aplica crea `companies/<slug>/STATUS.md`
9. ─→ ORQUESTADOR mem_save y reporta al usuario
```

### Formato de salida esperado

| Agente | Formato | Contenido |
|---|---|---|
| **@job-analyst** | Markdown | Empresa, rol, stack, seniority, ubicación, salario, fecha publicación, fit preliminar (pasa/no-pasa), señales de alerta |
| **@reviewer** | Markdown | Aprobado/Rechazado + razón principal + sugerencias de mejora + verificación de filtros duros |
| **@career-advisor** | Markdown | Análisis de tendencias, distribución de prioridades, ratio aplicación/entrevista, brechas de skill, recomendaciones |
| **job-matcher** (skill) | JSON estructurado | Technical Fit, Career Fit, Priority, green/red flags, difficulty, skill gaps, strengths, fórmula usada |

## 11. Skills vs. herramientas externas

| Herramienta | Cuándo usarla |
|---|---|
| **Skills** (`.opencode/skills/`) | Tareas procedurales del dominio job-search |
| **Playwright (local)** | Scraper de LinkedIn Jobs con sesión real (`scripts/linkedin-scraper.mjs`) |
| **`websearch`/`webfetch`** | Búsqueda multi-plataforma sin MCP (Himalayas, HN, RemoteOK, WWR, ATS) |
| **Engram** | Memoria persistente entre sesiones (mem_save, mem_search, mem_context) |
| **Composio MCP** | Solo para APIs externas no cubiertas (Gmail, etc.) — LinkedIn ya no usa Composio |

## 12. Validación y consistencia

- Ejecutar `bash scripts/validate-companies.sh` para verificar que todos los `companies/<slug>/STATUS.md` son consistentes (sin estados huérfanos)
- Consistencia cross-file: cada oferta en `data/jobs.csv` debe tener una entrada correspondiente en algún `data/daily/*.md`
- Engram `mem_doctor` para diagnosticar salud de la memoria
- Los ficheros `data/jobs.db`, `scripts/db.py` y `specs/architecture/persistence-data.md` son legacy de una migración a SQLite que no se completó — no se utilizan en el flujo activo
