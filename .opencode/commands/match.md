---
description: Evaluación individual de una oferta desde URL o descripción
---

Evalúa una oferta individual: `/match <url>` o `/match <descripción extensa>`.

### Flujo
1. Obtén la oferta (via `webfetch` si es URL, o usa el texto si es descripción).
2. Carga el subagente `@job-analyst` para extraer datos estructurados.
3. Carga la skill `job-matcher`.
4. Ejecuta evaluación dual (Technical Fit + Career Fit → Priority Score).
5. Si autorizado, persiste en `data/jobs.csv` vía skill `store-job` + escribe en `data/daily/YYYY-MM-DD.md`.
6. Muestra resultado completo como en `/search`.
