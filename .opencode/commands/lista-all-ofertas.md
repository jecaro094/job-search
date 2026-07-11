---
description: Lista todas las ofertas activas de la DB, consolidadas sin importar fecha de descubrimiento
---

Consulta directamente la base de datos SQLite (`data/jobs.db`) para obtener todas las ofertas activas y muestra tabla consolidada con estado de aplicación. No depende de ficheros legacy.

### Flujo

1. **Consulta la DB** usando `scripts/db.get_all_active_offers()` para obtener todas las ofertas con status 'active' o 'applied'.
2. **Para cada oferta**, consulta `scripts/db.get_application_status(slug)` para saber si hay candidatura y su estado actual.
3. **Consulta** `scripts/db.get_offers_by_priority()` para clasificar por rango.
4. **Agrupa por** verdict/prioridad (🚨≥85, 👍≥70, 🤔<70).
5. **Consolida descartes manuales**: consulta ofertas con status 'discarded' y, para cada discovery_date distinta, agrupa en tabla de descartes.


### Formato de salida

```
## 🎯 Ofertas totales

### 🚨 Apply immediately (Priority ≥85)
| # | Fecha | Empresa | Rol | Priority | URL | Fecha Oferta | Plataforma | Applied | Applied Date
|---|---------|-----|:--------:|-----|:----------:|:-:|
| 1 | DD-MM-YYY | Hack The Box | Senior Python Engineer | **100** | https://... | DD-MM-YYYY | Workable | - | -

### 👍 Apply (Priority ≥70)
| # | Fecha | Empresa | Rol | Priority | URL | Fecha Oferta | Plataforma | Applied | Applied Date
|---|---------|-----|:--------:|-----|:----------:|:-:|
| 1 | DD-MM-YYY | Kinxshn | Forward Deployed Engineer | **80** | mercedes@kinxshn.com | DD-MM-YYYY | HN | 🟡 | DD-MM-YYYY

### 🤔 Consider (Priority <70)
...misma estructura...

### ⏳ Pendientes de evaluar
| Fecha | Empresa | Rol | Plataforma |
|---------|-----|:----------:|
| DD-MM-YYY | Make Waves | Sr Full Stack Engineer | HN |

---

**Resumen**: X ofertas activas | 🚨 N | 👍 N | 🤔 N | ⏳ N | 🗑️ N descartadas manualmente

> Para aplicar a una oferta usa `/apply <empresa>`. Para ver detalle completo usa `/match <url>`.

### 🗑️ Descartadas manualmente (todos los logs)
| # | Log | Empresa | Rol | Razón descarte | Fecha descarte |
|---|:---:|---------|-----|----------------|:--------------:|
| 1 | 2026-07-11 | Enveritas | Backend SWE - Python/Postgres | No me interesa non-profit | 2026-07-11 |
```

### Consideraciones

- La DB garantiza dedup automático (hash determinista). Cada empresa+rol+url aparece una sola vez.
- Si una URL es un email, muéstralo como tal.
- Si no hay URL, muestra "No disponible" o "LinkedIn (caducó)".
- Si una oferta está ya en 🟢 Hot / 🟡 In progress, añade una nota de seguimiento.
- Las ofertas descartadas solo aparecen en la tabla de descartes, nunca en la principal.
- La sección `### Descartadas manualmente (todos los logs)` solo se muestra si tiene contenido. Si no hay descartes, se omite.
- La `fecha de la oferta` es el `posting_date` de la DB. No rellenar si es NULL.
- La `fecha` de descubrimiento es el `discovery_date` de la DB.
