---
description: Consulta el estado de una candidatura desde companies/<slug>/STATUS.md
---

Consulta el estado de una candidatura: `/estado-candidatura $ARGUMENTS`

### Parámetros
- `$ARGUMENTS`: nombre de la empresa (texto libre, case-insensitive)

### Flujo
1. Normaliza el nombre a slug (minúsculas, espacios a guiones, sin caracteres especiales).
2. **Lee `companies/<slug>/STATUS.md`** — si existe, muestra contenido completo con timeline.
3. **Si no existe en companies/**, busca en `data/jobs.csv` por coincidencia de nombre y lista las ofertas similares.
4. Si no hay nada, responde: "No encontré ninguna candidatura ni oferta para '$ARGUMENTS'."
