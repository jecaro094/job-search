---
description: Lista ofertas activas de un log diario con tabla detallada y estado de aplicación
mode: primary
---

Lee `data/daily/YYYY-MM-DD.md` y muestra tabla agrupada por rango de prioridad.

### Parámetros

| Parámetro | Descripción | Defecto |
|-----------|-------------|---------|
| `$ARGUMENTS` | Fecha en formato YYYY-MM-DD. Si no se pasa, usa hoy | Hoy |

### Flujo

1. Determina la fecha: si se pasó `$ARGUMENTS` válido, úsalo; si no, usa `date +%Y-%m-%d`.
2. Lee `data/daily/YYYY-MM-DD.md`. Si no existe, muestra error.
3. Extrae las ofertas de las secciones `### 🚨 TOP OFERTA — Priority ≥85`, `### 👍 Priority ≥70`, `### 🤔 Priority <70`.
4. Para cada oferta, busca en `data/jobs.csv` la fila correspondiente para obtener:
   - **Fecha de publicación** (`posting_date` columna si existe, o date de la fila)
   - Estado de aplicación (columna `status`: `discarded`, o `applied` si `applied` no está vacío)
   - Si no hay fecha de publicación → mostrar `-`
5. Cruza con `companies/<slug>/STATUS.md` para saber si existe candidatura y su estado (🟢 / 🟡 / 🔴 / ⚪).
6. **Filtra**: excluye ofertas con `status=discarded` en CSV (ya aparecen en tabla de descartes).

### Formato de salida

```
## 🎯 Ofertas del día — <YYYY-MM-DD>

### 🚨 Apply immediately (Priority ≥85)
| # | Empresa | Rol | Priority | 📅 Publicación | URL | Plataforma | Applied |
|---|---------|-----|:--------:|:--------------:|-----|:----------:|:-------:|
| 1 | Hack The Box | Sr Python Engineer | **100** | 2026-07-08 | https://... | Workable | - |
| 2 | Novakid School | Backend Python Dev | **98** | - | https://... | Himalayas | 🟡 |

### 👍 Apply (Priority ≥70 — <85)
| # | Empresa | Rol | Priority | 📅 Publicación | URL | Plataforma | Applied |
|---|---------|-----|:--------:|:--------------:|-----|:----------:|:-------:|
| 1 | AppFollow | Sr Backend Engineer | **83** | - | https://... | Lever | - |

### 🤔 Consider (Priority <70)
Misma estructura que arriba.

```

### Reglas para la columna 📅 Publicación

- ⚠️ **Siempre mostrar esta columna** en todas las tablas de ofertas.
- Si en `data/jobs.csv` la fila tiene `date` (fecha de evaluación/discovery) que coincide con cuando se publicó la oferta, usar esa fecha.
- Si se conoce la fecha de publicación real, mostrarla en formato `YYYY-MM-DD`.
- Si **no se conoce** la fecha de publicación, mostrar **`-`** (un guión).
- Esto aplica a todas las tablas: 🚨, 👍, 🤔, y descartes.

### 🗑️ Descartadas manualmente (si existen)

| # | Empresa | Rol | Razón descarte | Fecha descarte |
|---|---------|-----|----------------|:--------------:|
| 1 | Holafly | Sr Backend Engineer Python/Django | Oferta con ~4 meses de antigüedad | 2026-07-13 |

### Resumen

**X ofertas activas** | 🚨 N | 👍 N | 🤔 N | 🗑️ N descartadas

> Para aplicar: `/apply <empresa>`. Para ver detalle: `/match <url>`.
