---
description: Muestra el estado e información detallada de una candidatura de empresa
---

Obtén la información completa de una candidatura pasando el nombre de la empresa con: `/estado-candidatura $ARGUMENTS`

1. **Normaliza** el nombre a slug (minúsculas, sin acentos, espacios → guiones).
2. **Consulta la DB** usando `scripts/db.get_application_status(slug)`.
3. **Si no existe en DB**, busca ofertas en DB con `scripts/db.search_offers(query)` y lista las más similares.
4. **La información proviene de la DB**:
   - `applications` → estado actual y plataforma origen
   - `events` → timeline de eventos
   - `offers` → rol, stack, url, priority score
5. **NOTES.md y otros ficheros** en `companies/<slug>/` pueden contener información adicional (notas de entrevista, respuestas de formularios). Si existen, léelos también y combínalos.
6. **Preséntame un resumen estructurado** con:
   - **Estado** 🟢🟡🔴 (Hot / In progress / Descartado / En el limbo)
   - **Rol y stack técnico**
   - **Progreso del proceso** (etapas completadas vs. pendientes)
   - **Compensación** (si está disponible)
   - **Notas relevantes** (fit, observaciones, próximos pasos)
