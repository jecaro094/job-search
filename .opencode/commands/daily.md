---
description: Pipeline completo diario -> diagnóstico de companies desde DB, búsqueda multi-plataforma automática, LinkedIn opcional, evaluación dual y persistencia en SQLite
---

Ejecuta el pipeline completo de la rutina diaria:

### Fase 1 — Diagnóstico de candidaturas (desde DB)
1. Pregunta siempre: `Quieres que haga diagnostico de tus candidaturas?`, antes de ejecutar fase 1. Posibles respuestas:
    - Si
    - No
2. Consulta `scripts/db.get_status_summary()` para resumen agrupado por estado.
3. Para cada grupo (🟢 Hot / 🟡 In progress / ⚪ Limbo / 🔴 Descartado), consulta `scripts/db.get_all_applications(status_filter=...)` y muestra cada empresa con su último evento conocido (desde `events` table).

### Fase 2 — Búsqueda de ofertas
4. Carga la skill `multi-platform-search`. Busca en Himalayas, HN, RemoteOK, WWR, ATS, empresas objetivo. **Automático, sin preguntar.**

### Fase 3 — Evaluación y persistencia (en SQLite)
5. Unifica ofertas de todos los canales ejecutados.
6. Cross-check: si empresa está 🔴 Descartado en DB → preguntar antes de evaluar.
7. Carga la skill `job-matcher`. Evalúa cada oferta con scoring dual (Technical Fit + Career Fit → Priority). Para ello emplea el subagente `job-analyst`.
8. Muestra TOP ofertas: 🚨≥85, 👍≥70, 🤔<70. Para Priority≥85 pregunta si aplicar.
9. **Persiste en DB** usando `scripts/db.insert_offer()` + `scripts/db.insert_event()`.
   - El CSV (`data/jobs.csv`) ya no se escribe directamente. Se regenera bajo demanda.
   - El log diario (`data/daily/YYYY-MM-DD.md`) ya no se escribe. La información está en la DB.
   - El RAW JSON en `data/search/YYYY-MM-DD/` sigue siendo opcional para debug.
10. Resumen final: canales buscados, ofertas evaluadas, distribución por rango.
11. Si hay Priority≥85 → pregunta "¿Quieres que prepare la aplicación?"
