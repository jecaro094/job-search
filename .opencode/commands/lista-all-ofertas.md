---
description: Lista todas las ofertas activas de todos los logs diarios consolidados
mode: primary
---

Escanea **todos** los archivos `data/daily/YYYY-MM-DD.md` y consolida las ofertas activas en una sola tabla agrupada por prioridad.

### Flujo

1. Busca todos los archivos `data/daily/*.md`.
2. Para cada archivo, extrae las ofertas de las secciones de prioridad.
3. Para cada oferta, busca en `data/jobs.csv` la fila correspondiente para obtener:
   - **Fecha de publicación** — si se conoce, mostrarla. Si no, `-`.
   - Estado actual (discarded, o si `applied` no vacío → candidatura registrada)
4. Cruza con `companies/<slug>/STATUS.md` para estado de candidatura (🟢 / 🟡 / 🔴 / ⚪).
5. **Excluye** ofertas con `status=discarded` en CSV (van a tabla de descartes).
6. **Dedup**: misma empresa+rol → mostrar solo la más reciente.

### Formato de salida

```
## 🎯 Ofertas totales (consolidadas)

### 🚨 Apply immediately (Priority ≥85)
| # | 📅 Discovery | Empresa | Rol | Priority | 📅 Publicación | URL | Plataforma | Applied |
|---|:-----------:|---------|-----|:--------:|:--------------:|-----|:----------:|:-------:|
| 1 | 2026-07-13 | VOYGR | Full-Stack Engineer | **100** | 2026-07-13 | https://... | YC | - |
| 2 | 2026-07-11 | Kalepa | Sr Backend Engineer | **99** | 2026-07-11 | https://... | Himalayas | - |

### 👍 Apply (Priority ≥70 — <85)
| # | 📅 Discovery | Empresa | Rol | Priority | 📅 Publicación | URL | Plataforma | Applied |
|---|:-----------:|---------|-----|:--------:|:--------------:|-----|:----------:|:-------:|
| 1 | 2026-07-13 | AppFollow | Sr Backend Engineer | **83** | - | https://... | Lever | - |

### 🤔 Consider (Priority <70)
Misma estructura.

```

### Reglas para la columna 📅 Publicación

- ⚠️ **Siempre mostrar esta columna** en todas las tablas de ofertas.
- Usar la fecha de publicación real si está disponible en CSV o en el log diario.
- Si **no se conoce**, mostrar **`-`**.
- Aplica a todas las tablas (🚨, 👍, 🤔, descartes).

### 🗑️ Descartadas manualmente (todos los logs)

| # | 📅 Log | Empresa | Rol | Razón descarte | Fecha descarte |
|---|:-----:|---------|-----|----------------|:--------------:|
| 1 | 2026-07-13 | Holafly | Sr Backend Engineer Python/Django | Oferta con ~4 meses de antigüedad | 2026-07-13 |

### Resumen

**X ofertas activas totales** | 🚨 N | 👍 N | 🤔 N | 🗑️ N descartadas

> Para aplicar: `/apply <empresa>`. Para ver detalle: `/match <url>`.
