---
description: Pipeline completo diario -> diagnóstico de companies desde ficheros, búsqueda multi-plataforma automática (incluye LinkedIn vía web search), evaluación dual y persistencia en data/
---

Ejecuta el pipeline completo de la rutina diaria:

### Fase 1 — Diagnóstico de candidaturas (desde ficheros)
1. Pregunta siempre: `Quieres que haga diagnostico de tus candidaturas?`, antes de ejecutar fase 1. Posibles respuestas:
    - Si
    - No
2. Lee `companies/*/STATUS.md` para resumen agrupado por estado:
   - Extrae el estado de cada empresa (🟢 Hot / 🟡 In progress / ⚪ Limbo / 🔴 Descartado)
   - Extrae el último evento del timeline de cada una
3. Muestra resumen agrupado y detecta candidaturas estancadas (>14d sin movimiento).

### Fase 2 — Búsqueda de ofertas
4. Carga la skill `multi-platform-search`. Busca en Himalayas, HN, RemoteOK, WWR, ATS, empresas objetivo. **Automático, sin preguntar.**

### Fase 3 — Evaluación y persistencia (en ficheros)
5. Unifica ofertas de todos los canales ejecutados.
6. Cross-check: si `companies/<slug>/STATUS.md` tiene estado 🔴 Descartado → preguntar antes de evaluar.
7. Carga la skill `job-matcher`. Evalúa cada oferta con scoring dual (Technical Fit + Career Fit → Priority). Para ello emplea el subagente `job-analyst`.
8. Muestra TOP ofertas: 🚨≥85, 👍≥70, 🤔<70. Para Priority≥85 pregunta si aplicar.
9. **Persiste en ficheros**:
   - Appendea a `data/jobs.csv` con el skill `store-job` (una fila por oferta evaluada).
   - Escribe log diario en `data/daily/YYYY-MM-DD.md` con detalle de cada evaluación.
   - Si aplicas, crea `companies/<slug>/STATUS.md` con estado 🟡 In progress.
10. Resumen final: canales buscados, ofertas evaluadas, distribución por rango.
11. Si hay Priority≥85 → pregunta "¿Quieres que prepare la aplicación?"
