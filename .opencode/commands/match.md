---
description: Evalúa una oferta específica (URL o descripción) contra el perfil y la CV
---

Recibe una URL o descripción de LinkedIn y:

1. Pasa la oferta al subagente @job-analyst para extracción y filtrado (usa `webfetch` o la descripción directa).
2. Si pasa filtros, carga la skill `job-matcher` para evaluación técnica.
3. Si pasa filtros, carga la skill `job-matcher` para evaluación técnica.
4. Pasa el resultado a @reviewer para validación.
5. Si autorizado, persiste en `data/jobs.db` vía skill `store-job` (que usa `scripts/db.insert_offer()`).
6. Dame un veredicto claro: **fit** o **mismatch** y los 3 motivos principales.
