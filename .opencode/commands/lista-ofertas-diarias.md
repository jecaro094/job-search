---
description: Lista todas las ofertas relevantes evaluadas en una fecha desde la DB, con URLs y campos clave para decidir acción
---

Lee de la base de datos SQLite (`data/jobs.db`) las ofertas descubiertas en una fecha y las muestra en tabla, incluyendo estado de aplicación.

### Parámetros

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `$ARGUMENTS` | Fecha opcional en formato YYYY-MM-DD. Si no se pasa, usa la fecha de hoy. | Hoy |

### Flujo

1. **Determina la fecha**: si se pasó `$ARGUMENTS` válido (YYYY-MM-DD), úsalo; si no, usa la fecha de hoy.
2. **Consulta la DB** usando `scripts/db.get_offers_by_date(fecha)`. Si no hay ofertas para esa fecha, muestra error.
3. **Para ofertas activas**, consulta además `scripts/db.get_application_status(slug)` para saber si hay candidatura y su estado.
4. **Filtra** solo ofertas **activas** (status = 'active' en DB):
   - Excluye ofertas con status 'discarded', 'expired' o 'closed'
   - Incluye:
     - 🎯 Apply immediately (Priority ≥85)
     - 👍 Apply (Priority ≥70)
     - 🤔 Consider (Priority <70)
5. **Agrupa por** verdict/prioridad.
6. En la tabla resumen de salida, poner en la columna `Applied`: NO (-) / YES (estado descartado 🔴 / in progress 🟡 / hot 🟢)
7. En la columna `Applied Date`, poner la fecha en que se aplicó (formato DD-MM-YYYY) si existe candidatura en DB (events con event_type='applied'). Si no se ha aplicado, poner `-`.
10. Si existen ofertas en `### Descartadas manualmente`, añade una sección al final con la tabla de descartes.

### Formato de salida

```
## 🎯 Ofertas del día — <fecha>

### 🚨 Apply immediately (Priority ≥85)
| # | Empresa | Rol | Priority | URL | Fecha | Plataforma | Applied | Applied Date
|---|---------|-----|:--------:|-----|:----------:|:-:|
| 1 | Hack The Box | Senior Python Engineer | **100** | https://... | DD-MM-YYYY | Workable | - | -

### 👍 Apply (Priority ≥70)
| # | Empresa | Rol | Priority | URL | Fecha | Plataforma | Applied | Applied Date
|---|---------|-----|:--------:|-----|:----------:|:-:|
| 1 | Kinxshn | Forward Deployed Engineer | **80** | mercedes@kinxshn.com | DD-MM-YYYY | HN | 🟡 | DD-MM-YYYY

### 🤔 Consider (Priority <70)
...misma estructura...

### ⏳ Pendientes de evaluar
| Empresa | Rol | Plataforma |
|---------|-----|:----------:|
| Make Waves | Sr Full Stack Engineer | HN |

---

**Resumen**: X ofertas activas | 🚨 N | 👍 N | 🤔 N | ⏳ N | 🗑️ N descartadas manualmente

> Para aplicar a una oferta usa `/apply <empresa>`. Para ver detalle completo usa `/match <url>`.

### 🗑️ Descartadas manualmente
| # | Empresa | Rol | Razón descarte | Fecha descarte |
|---|---------|-----|----------------|:--------------:|
| 1 | Enveritas | Backend SWE - Python/Postgres | No me interesa non-profit | 2026-07-11 |
```

### Consideraciones

- La DB ya garantiza dedup por hash determinista (misma empresa+rol+url → mismo ID).
- Si una URL es un email, muéstralo como tal.
- Si no hay URL, muestra "No disponible" o "LinkedIn (caducó)".
- Si una oferta está ya en 🟢 Hot / 🟡 In progress, añade una nota de seguimiento.
- Si hay ofertas descartadas (status = 'discarded'), no las muestres en la tabla principal.
- Las ofertas descartadas con `discard_offer()` se muestran siempre en la tabla de descartes manuales al final.
- La fecha que aparezca en las tablas resultado sería la `posting_date` de la oferta. No rellenar si no se sabe.
- La sección `### Descartadas manualmente` solo se muestra si tiene contenido. Si no hay descartes, se omite.
- Puedes regenerar la vista legacy desde DB con: `sqlite3 data/jobs.db ".mode csv" "SELECT * FROM offers" > data/jobs.csv`
