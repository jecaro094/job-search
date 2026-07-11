---
description: Búsqueda multi-plataforma automática (Himalayas, HN, RemoteOK, WWR, ATS) + evaluación dual + log diario. Alias: /search
---

Ejecuta la búsqueda proactiva multi-plataforma definida en `specs/features/job-search.md`. Comando: `/search`:

### Canales automáticos (todos sin preguntar)
1. Carga la skill `multi-platform-search`. Escanea:
   - Himalayas (API — 4 queries: backend, api, data, senior backend)
   - HN "Who is hiring" vía hnhiring.com
   - RemoteOK
   - We Work Remotely
   - ATS (Greenhouse, Lever, Workable, Ashby, Recruitee)
   - Empresas objetivo
2. **Pregunta**: "¿Quieres buscar también en LinkedIn? (tarda 3-5 minutos)" [s/N].

### Evaluación y persistencia (en SQLite)
3. Unifica ofertas de todos los canales ejecutados.
4. Cross-check: si empresa está 🔴 Descartado en DB → preguntar antes de evaluar.
5. Carga la skill `job-matcher`. Evalúa cada oferta con scoring dual.
6. Muestra TOP ofertas agrupadas por rango (🚨≥85, 👍≥70, 🤔<70).
7. **Persiste en SQLite** usando:
   - `scripts/db.insert_offer()` para cada oferta evaluada
   - `scripts/db.insert_event()` para el timeline de evaluación
   - Raw JSON opcional en `data/search/YYYY-MM-DD/` (solo para debug)
8. Resumen final: canales buscados, ofertas evaluadas, distribución por rango.
