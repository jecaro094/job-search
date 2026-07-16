# Roadmap

## Fase 1: Fundación ✅
- [x] AGENTS.md con instrucciones base
- [x] CV estructurado (cv/cv.md)
- [x] Skills: job-matcher, multi-platform-search, store-job, prepare-interview, show-applied-jobs
- [x] data/jobs.csv tracker
- [x] companies/ con estado por empresa
- [x] Engram configurado como MCP

## Fase 2: Modularización (actual)
- [x] `.opencode/agents/core/` — agente orquestador
- [x] `.opencode/agents/subagents/` — job-analyst, reviewer
- [x] `.opencode/commands/` — /search, /match, /apply
- [x] `.opencode/context/` — filtros, stack, preferencias como patrones @
- [x] `specs/constitution/` — misión y roadmap
- [x] `specs/features/` — specs de funcionalidades clave
- [x] `tasks/` — tracking de progreso visible

## Fase 3: Automatización ✅
- [x] **Script de validación** (`scripts/validate-companies.sh`) — chequea consistencia de companies/
- [x] **Rutina diaria** (`scripts/daily.sh` + comando `/daily`) — validación + recordatorios cada mañana
- [x] **Spec de arquitectura** (`specs/architecture/agent-architecture.md`) — documenta skills vs subagentes, protocolos, fuentes de verdad
- [x] **show-applied-jobs** reescrito — ahora lista desde `companies/` (ficheros), no desde Engram
- [ ] CI/CD en `.github/workflows/` para recordatorios semanales
- [ ] Notificaciones al usuario de nuevas ofertas top
- [ ] Dashboard semanal con métricas (ofertas/mes, fit rate, aplicación rate)
- [ ] Análisis de tendencias: qué stacks piden más, qué empresas contratan

## Fase 4: Refinamiento
- [ ] Feedback loop: cuando el usuario rechaza una oferta, aprender para futuros filtros
- [ ] Detección automática de empresas ya contactadas (evitar duplicados)
- [ ] Score histórico: qué tipo de empresas le han hecho oferta
