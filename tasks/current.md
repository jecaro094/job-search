# Tareas actuales

> ⏱ Actualizado: 2026-07-22 (Veriff Stage 3 agendada para 31 Jul)

---

## Fase 1: Fundación ✅

- [x] AGENTS.md con instrucciones base
- [x] CV estructurado (cv/cv.md)
- [x] Skills base: store-job, prepare-interview, show-applied-jobs, multi-platform-search
- [x] data/jobs.csv tracker
- [x] companies/ con estado por empresa (126 empresas)
- [x] Engram configurado como MCP

## Fase 2: Modularización ✅

- [x] `.opencode/agents/core/` — agente orquestador
- [x] `.opencode/agents/subagents/` — job-analyst, reviewer, career-advisor
- [x] `.opencode/commands/` — /search, /match, /apply
- [x] `.opencode/context/` — filtros, stack, preferencias como patrones @
- [x] `specs/constitution/` — misión y roadmap
- [x] `specs/features/` — specs de funcionalidades clave
- [x] `tasks/` — tracking de progreso visible

## Fase 2.5: Arquitectura y consistencia ✅

- [x] Spec de arquitectura (`specs/architecture/agent-architecture.md`)
- [x] Skills vs Subagentes clarificado en AGENTS.md
- [x] Script de validación (`scripts/validate-companies.sh`)
- [x] Rutina diaria (`scripts/daily.sh` + comando `/daily`)

---

## 🟢 Fase 3: Scoring Dual — COMPLETADA ✅

### Mejoras implementadas (10 áreas)

| # | Mejora | Archivos |
|---|--------|----------|
| 1 | **Scoring dual** (Technical Fit + Career Fit → Priority Score) | `specs/features/scoring-dual.md`, `job-matcher/SKILL.md`, `criteria.md` |
| 2 | **Green flags** (12 señales positivas, máx +30) | `criteria.md`, `job-matcher/SKILL.md`, `multi-platform-search/SKILL.md` |
| 3 | **Red flags** (13 señales de alerta, máx -40) | `criteria.md`, `job-matcher/SKILL.md`, `multi-platform-search/SKILL.md` |
| 4 | **Filtros binarios reducidos** (solo 5 duros). Fecha y tipo empresa → scoring gradual | `filters.md`, `AGENTS.md`, `criteria.md` |
| 5 | **Dificultad estimada** (Easy / Medium / Hard) | `job-matcher/SKILL.md`, `criteria.md` |
| 6 | **Multi-plataforma detection** (apariciones en 2+ fuentes → bonus) | `multi-platform-search/SKILL.md` |
| 7 | **Pre-scan ahorrador** (red flags obvias → omitir job-matcher) | `multi-platform-search/SKILL.md` |
| 8 | **Prioritización por Priority Score** | Automático en job-matcher |
| 9 | **Career-advisor subagent** (tendencias, conversión, feedback loop) | `agents/subagents/career-advisor.md` |
| 10 | **CSV extendido** (nuevas columnas: technical_fit, career_fit, priority, green/red flags, difficulty, platforms) | `store-job/SKILL.md` |

### Archivos creados o modificados
- ✅ `specs/features/scoring-dual.md` — spec completo del nuevo scoring
- ✅ `.opencode/context/core/criteria.md` — pesos duales, green/red flags, dificultad, fórmula
- ✅ `.opencode/context/project/filters.md` — solo 5 cortes binarios, el resto es scoring
- ✅ `.opencode/skills/job-matcher/SKILL.md` — reescrito con dual scoring
- ✅ `.opencode/skills/store-job/SKILL.md` — nuevas columnas + dedup
- ✅ `.opencode/skills/multi-platform-search/SKILL.md` — multi-plataforma + pre-scan
- <span style="opacity:0.4">~~`.opencode/skills/weekly-ranking/SKILL.md` — nuevo skill~~</span> (dado de baja)
- ✅ `.opencode/agents/subagents/reviewer.md` — actualizado para dual scoring
- ✅ `.opencode/agents/subagents/career-advisor.md` — nuevo subagente
- ✅ `AGENTS.md` — actualizado (v2 Dual Scoring)
- ✅ `specs/architecture/agent-architecture.md` — actualizado con nuevo ciclo

---

## 🟢 Completado — Persistencia de búsquedas (2026-07-10)

| # | Mejora | Archivos |
|---|--------|----------|
| 1 | **Capa 1: resultados brutos** — cada búsqueda guarda JSONs por canal en `data/search/YYYY-MM-DD/HH-MM-{channel}.json` con todas las URLs empresas y razones de descarte | `specs/features/search-persistence.md`, `scripts/save-search-results.sh` |
| 2 | **Capa 2: APPEND diario** — el daily log ahora **acumula** secciones en vez de sobrescribir. Cada búsqueda añade `## Búsqueda HH:MM` | `specs/features/daily-log.md`, `specs/features/job-search.md` |
| 3 | **Capa 3: CSV robusto** — añadidas 5 evaluaciones faltantes (Veriff 93, Canonical 78, Saphetor 73, Lodgify 67, DeepSea 78) | `data/jobs.csv` |
| 4 | **Rotación automática** — script `rotate-search-data.sh` comprime datos >30 días | `scripts/rotate-search-data.sh` |
| 5 | **Archivo retrospectivo** — reconstruidos datos de las 3 búsquedas de hoy desde memoria de sesión | `data/search/2026-07-10/` (7 archivos), `data/daily/2026-07-10.md` (3 secciones) |
| 6 | **AGENTS.md actualizado** — nueva automatización A5 Search Persistence | `AGENTS.md` |

## 🟡 Activo — Operaciones en curso

### Candidaturas activas (3 🟢 Hot, ~62 🟡 In progress, 15 ⚪ Limbo)

| Empresa | Estado | Último evento |
|---------|--------|---------------|
| **Affirm** | 🟢 Hot | 🎯 Stage 1 agendada — **lunes 13 Jul, 12:00-12:30** |
| **Veriff** | 🟢 Hot | 🎯 Stage 3 (Arquitectura) agendada — **viernes 31 Jul, 12:00-13:30** |
| **Law Business Research** | 🟢 Hot | Stage 1 ✅ con Ramon (Manfred). Próximo update ~15 jul |
| **Novakid School** | 🟡 In progress | Aplicada — Priority 98/100. Stack idéntico (FastAPI, PostgreSQL, Redis, Celery) |
| **Black Swans** | 🟡 In progress | Aplicada vía LinkedIn |
| **MoneyHash** | 🟡 In progress | Aplicada — Priority 97/100. Stack perfecto (Django/DRF/PostgreSQL/Redis/K8s) |
| **Dwelly** 🆕 | 🟡 In progress | Priority 100/100 — Data Migration Platform. Q&A guardado. Pendiente enviar. |
| **Fundamental** 🆕 | 🟡 In progress | Priority 99/100 — ex-DeepMind. Backend Engineer Extensions. |
| **Scalera** 🆕 | 🟡 In progress | Priority 97/100 — ETH spin-off. Senior Backend Engineer (Python). |
| **Booksy** 🆕 | 🟡 In progress | Mid Software Engineer (Python). Aplicada vía LinkedIn. |
| ~60 más | 🟡 In progress | Importadas desde Notion kanban |
| 15 | ⚪ En el limbo | Sin movimiento |
| ~47 | 🔴 Descartadas | Documentadas con feedback |

---

## 🤖 Automatizaciones activas (implementadas 2026-07-10)

| # | Automatización | Estado | Cómo funciona |
|---|---------------|--------|---------------|
| 1 | **Auto-daily al inicio de sesión** | ✅ Activo | Primera acción de cada sesión: `/daily` con validación + candidaturas + recordatorios + entrevistas + **Pipeline A3** (follow-up estancadas) + **búsqueda proactiva** (si ≥12h desde última búsqueda) |
| 2 | **Auto-prepare-interview** | ✅ Activo | `scripts/check-upcoming-interviews.sh` escanea fechas futuras en STATUS.md. Según urgencia: ≥48h recordatorio, <48h ofrecer preparación, mismo día briefing |
| 3 | **Notificación ofertas top** | ✅ Activo | Priority ≥85 → `🚨 TOP OFERTA` con énfasis + pregunta de aplicación. Priority ≥70 → listado normal |
| 4 | **Cross-check descartadas** | ✅ Activo | Antes de evaluar cualquier oferta, se comprueba `companies/<slug>/STATUS.md`. Si está Descartado → se pregunta al usuario |
| 5 | **Detección entrevistas próximas** | ✅ Activo | Integrado en `scripts/daily.sh` vía `check-upcoming-interviews.sh` |
| 6 | **Pipeline A3 — Follow-up estancadas** | ✅ Activo | Detecta 🟡 In progress sin movimiento >14d y sugiere follow-up o paso a limbo. También escanea ⚪ Limbo >30d para descarte definitivo |

## 📋 Reglas operacionales activas

- [x] **Estado por defecto**: toda nueva candidatura se registra como 🟡 In progress
- [x] **Aviso de descartadas**: si oferta nueva coincide con empresa ya descartada, avisar
- [x] **Ficheros primero**: en consultas de empresa, leer `companies/<slug>/`
- [x] **Tasks persistido**: este fichero se actualiza tras cada operación importante
- [x] **Scoring dual**: toda evaluación usa Technical Fit + Career Fit → Priority
- [x] **Green/Red flags**: detectar siempre en cada evaluación
- [x] **Priorizar por Priority Score**: no por match técnico solo

---

## 🟡 Mejoras de cobertura implementadas (2026-07-10)

| # | Mejora | Archivos |
|---|--------|----------|
| 1 | **Búsqueda multi-plataforma** — Himalayas, HN, RemoteOK, WWR, ATS, empresas objetivo | `.opencode/skills/multi-platform-search/SKILL.md` |
| 2 | **Búsqueda en ATS** — Greenhouse, Lever, Workable, Ashby, Recruitee. Captura ofertas no indexadas en agregadores | `.opencode/skills/multi-platform-search/SKILL.md` |
| 3 | **Auto-daily con búsqueda proactiva** — al iniciar sesión, si pasaron ≥12h desde última búsqueda, ejecuta `/search` automáticamente | `AGENTS.md` |

---

## 🟢 Completado — Daily Evaluation Log (2026-07-10)

| # | Mejora | Archivos |
|---|--------|----------|
| 1 | **Log diario automático** — tras cada `/search`, `/match`, se guarda el log completo en `data/daily/YYYY-MM-DD.md` con desglose de Technical Fit, Career Fit, Green/Red Flags, Difficulty y Priority Score | `AGENTS.md`, `multi-platform-search/SKILL.md` |
| 2 | **Formato estructurado** — tabla de factores con peso × score, adjustments, flags, fórmula del Priority Score paso a paso | `data/daily/2026-07-10.md` (ejemplo real) |
| 3 | **Trazabilidad completa** — el usuario puede revisar en qué se basó cada evaluación sin depender de memoria de sesión | `AGENTS.md` (sección F) |

## 🟢 Completado — Refactor AGENTS.md a Spec-Driven (2026-07-10)

| # | Mejora | Archivos |
|---|--------|----------|
| 1 | **AGENTS.md simplificado** — de 236 a 126 líneas. Pipelines movidos a specs | `AGENTS.md` |
| 2 | **Specs actualizados** — `job-search.md` y `job-matching.md` reescritos con dual scoring | `specs/features/job-search.md`, `specs/features/job-matching.md` |
| 3 | **Daily Log spec** — nuevo spec con formato del log diario | `specs/features/daily-log.md` |

## 🟢 Completado — Mejora de descubrimiento (2026-07-10)

| # | Mejora | Archivos |
|---|--------|----------|
| 1 | **HN "Who is hiring"** — nuevo canal de búsqueda en el hilo mensual (300-500 ofertas, 100% activas) | `specs/features/job-search.md`, `multi-platform-search/SKILL.md` |
| 2 | **Wellfound / YC Work at a Startup** — startups con funding, remote-first, no indexadas en LinkedIn | `specs/features/job-search.md`, `multi-platform-search/SKILL.md` |
| 3 | **Búsqueda por empresas objetivo** — 40+ empresas priorizadas por categoría (fintech, data, infra, SaaS, healthcare, marketplaces, Europe, open source) buscando directamente en sus ATS | `specs/features/job-search.md`, `multi-platform-search/SKILL.md` |
| 4 | **Pipeline A3 — Follow-up estancadas** — detecta 🟡 In progress sin movimiento >14d y ⚪ Limbo >30d | `specs/features/job-search.md`, `AGENTS.md` |
| 5 | **Auditoría companies/** — 45 empresas sin fecha verificadas (todas ya 🔴 Descartado). 6 🟡 In progress viejas identificadas | `specs/features/job-search.md` |

---

### Nuevas TOP ofertas evaluadas (15:30)

| Empresa | Rol | Priority | Estado |
|---------|-----|:--------:|--------|
| Hack The Box | Sr Python Engineer | **100** 🎯 | Persistida, pendiente aplicar |
| MoneyHash | Sr Backend Engineer | **97** 🎯 | 🟡 In progress — candidatura registrada + Q&A guardado |
| Qonto AI LAB | Sr Backend Engineer | **89** 🎯 | Persistida, pendiente aplicar |
| Jobgether Spain | Sr Python Backend Developer | **85** 🎯 | Persistida, pendiente aplicar |

**Cross-check pendiente**: SPD Technology (🔴 → ¿reconsiderar?), Somnio Software (⚪ → ¿evaluar?)
**Stale companies**: ~50 "In progress" sin movimiento → preguntar si pasar a limbo
**Entrevista inminente**: Affirm — lun 13 Jul 12:00-12:30. Ofrecer prep.
**Ashby pendientes**: ✅ Scalera (❌ 87d recencia) + Synthflow (❌ hybrid Berlín) — evaluadas y archivadas

---

## 🔲 Pendiente (Fase 4+)

- [ ] CI/CD con recordatorios semanales (`.github/workflows/`)
- [ ] Dashboard de métricas (ofertas/mes, fit rate, aplicación rate)
- [ ] Feedback loop: aprender de ofertas rechazadas para ajustar filtros
- [ ] Análisis de tendencias: qué stacks se piden más
- [ ] Primer informe del @career-advisor
