# Feature: Persistencia de resultados de búsqueda

## Propósito

Guardar **todos los resultados brutos de búsqueda** (no solo las evaluaciones finales) en archivos persistentes, para que no se pierdan entre sesiones ni se sobrescriban.

Cada búsqueda se guarda en **3 capas** con distinto nivel de detalle:

| Capa | Ruta | Contenido | Se genera |
|------|------|-----------|-----------|
| 1 — Raw | `data/search/YYYY-MM-DD/HH-MM-{channel}.json` | Resultados brutos por canal: todas las URLs, snippets, disposición, motivo | Inmediatamente después de obtener resultados, antes de filtrar |
| 2 — Daily log | `data/daily/YYYY-MM-DD.md` | Resumen estructurado con job-matcher completo, descartadas, métricas | Después de evaluar y validar, antes de store-job |
| 3 — CSV | `data/jobs.csv` | Evaluaciones finales (solo las que pasaron @reviewer) | Después del daily log |

## Capa 1 — Resultados brutos por canal

### Estructura de directorios

```
data/search/YYYY-MM-DD/HH-MM-{channel}.json
```

Canales posibles: `linkedin`, `himalayas`, `remoteok`, `wwr`, `ats`, `hn`, `wellfound`, `yc`, `target-companies`, `catchall`, `individual-match`.

### Formato JSON exhaustivo

Cada archivo JSON debe contener **todos** los datos disponibles de cada oferta:

```json
{
  "timestamp": "2026-07-10T13:07:00+02:00",
  "channel": "linkedin",
  "pipeline": "search",
  "queries_executed": [
    "site:linkedin.com/jobs \"python\" \"backend\" remote posted past week"
  ],
  "total_found": 40,
  "results": [
    {
      "company": "Hire Feed",
      "title": "Python Developer (Remote) - NAMER",
      "url": "https://www.linkedin.com/jobs/view/123456789",
      "snippet": "Looking for a Python Developer with 5+ years experience...",
      "disposition": "rejected",
      "reason": "Location: NAMER only",
      "filter_failed": "location"
    }
  ],
  "metrics": {
    "total": 40,
    "passed_prefilters": 0,
    "evaluated": 0,
    "rejected": {
      "location": 28,
      "contract": 5,
      "recency": 3,
      "role": 4
    }
  }
}
```

### Reglas para la Capa 1

1. **URL**: siempre incluir la URL completa y verificable. Si no hay URL, indicar "No disponible".
2. **Snippet**: incluir el texto del snippet si está disponible (ayuda a entender por qué se descartó).
3. **Disposición**: `evaluated`, `rejected`, `duplicate`, `already_exists`.
4. **filter_failed**: para ofertas rechazadas, indicar qué filtro falló (`location`, `contract`, `recency`, `role`, `python`, `remote`).
5. **Se guarda antes de evaluar**: los resultados brutos se persisten inmediatamente después de obtenerlos, antes de aplicar filtros o evaluar. Esto garantiza que, aunque la sesión se interrumpa, los datos no se pierden.

## Capa 2 — Daily log

Ver `specs/features/daily-log.md` para el formato exhaustivo.

## Capa 3 — CSV

Sin cambios respecto al spec actual de `store-job`.

## Flujo de ejecución (orden obligatorio)

```
1. Obtener resultados de un canal
2. GUARDAR RAW en data/search/YYYY-MM-DD/HH-MM-{channel}.json   ← Capa 1
3. Aplicar pre-filtros (5 cortes binarios)
4. Evaluar con job-matcher (scoring dual)
5. Validar con @reviewer
6. APPEND sección al daily log                                       ← Capa 2
7. store-job → data/jobs.csv                                         ← Capa 3
```

**Nunca** se salta el paso 2. Los resultados brutos se guardan siempre, incluso si luego todas las ofertas son descartadas.

## Rotación

- Los archivos `data/search/` se conservan **30 días** (luego se comprimen a `.tar.gz`).
- `data/daily/` y `data/jobs.csv` se conservan **indefinidamente**.
- El script `scripts/rotate-search-data.sh` se ejecuta semanalmente.

## Responsabilidad

El orquestador (`@primary`) es responsable de:
1. Guardar los resultados brutos en `data/search/` **inmediatamente después** de obtenerlos.
2. Hacer APPEND al daily log con el formato exhaustivo **después** de evaluar.
3. Llamar a `store-job` para las evaluaciones finales.
