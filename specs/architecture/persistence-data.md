# Arquitectura de Persistencia (SQLite)

## 1. Principios

| Principio | Descripción |
|---|---|
| **DB como fuente de verdad única** | Toda la información de ofertas, evaluaciones, candidaturas y eventos se almacena en `data/jobs.db`. No hay dual write. |
| **Hash determinista como PK** | Cada oferta tiene un ID = `sha256(company + role + url)[:16]`. Misma combinación → mismo registro siempre. |
| **Upsert, no append** | `INSERT OR REPLACE` evita duplicados. Si se re-evalúa una oferta, se actualiza con los nuevos scores. |
| **Engram = contexto, no datos** | Engram guarda solo decisiones, patrones, preferencias, gotchas. Los datos estructurados (scores, fechas, estados) van a SQLite. |
| **Sin ficheros legacy** | `data/jobs.csv`, `data/daily/*.md`, `companies/*/STATUS.md` ya no se escriben. Se regeneran bajo demanda desde la DB con `sqlite3` export o scripts ad-hoc. |

---

## 2. Schema relacional

```
┌─────────────────────────────────────────────────────────────────┐
│                        offers                                    │
│  PK: id (hash)                                                  │
│  company, role, url, platform, posting_date, discovery_date     │
│  tech_fit, career_fit, priority                                  │
│  green_flags, red_flags, difficulty, verdict, summary            │
│  source_platforms, status                                         │
│  created_at, updated_at                                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ 1
                           │
                  ┌────────▼────────┐
                  │    events       │ (N por offer)
                  │  FK: offer_id   │
                  │  event_type     │
                  │  detail         │
                  │  metadata (JSON)│
                  └─────────────────┘
                           │ 1
                           │
                  ┌────────▼────────┐
                  │  applications   │ (0..1 por offer)
                  │  PK: offer_id   │
                  │  status         │
                  │  source_platform│
                  │  notes          │
                  │  created_at     │
                  └─────────────────┘

┌───────────────────────────────────────────┐
│           search_rounds                    │
│  Métricas de cada pipeline ejecutado       │
│  search_date, platform, offers_scanned...  │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│           learnings                        │
│  Backups de Engram (por si se pierde)      │
│  category, title, body, synced_to_engram   │
└───────────────────────────────────────────┘
```

### 2.1 Tabla `offers`
Registro central de cada oferta descubierta y evaluada.

- **PK**: hash determinista de `company+role+url` (16 chars hex)
- **Status** posibles: `active`, `applied`, `discarded`, `expired`, `closed`
- **Verdicts**: `Apply immediately`, `Apply`, `Consider`, `Skip`
- **Índices**: status, priority DESC, company_slug, discovery_date DESC

### 2.2 Tabla `events`
Timeline de cada oferta. Un evento por acción significativa.

- **Tipos**: `discovered`, `evaluated`, `re-evaluated`, `applied`, `interview_scheduled`, `interview_done`, `rejected`, `accepted`, `discarded`, `expired`, `manual_note`
- FK a `offers(id)` con `ON DELETE CASCADE`

### 2.3 Tabla `applications`
Candidatura activa para una oferta (0..1 por offer).

- **Status**: `hot`, `in_progress`, `limbo`, `descartado`
- FK a `offers(id)` con `ON DELETE CASCADE`

### 2.4 Tabla `search_rounds`
Métricas agregadas de cada ejecución de búsqueda (para el career-advisor).

### 2.5 Tabla `learnings`
Copia de seguridad de observaciones importantes. Sincronizada con Engram.

---

## 3. API de acceso (`scripts/db.py`)

```
scripts/
└── db.py                 ← Helper con 12 funciones de lectura/escritura
    ├── get_conn()        ← Conexión SQLite (row_factory=Row, FK on)
    ├── offer_id()        ← Hash determinista
    ├── insert_offer()    ← Upsert de oferta + evento "evaluated"
    ├── insert_event()    ← Añadir evento al timeline
    ├── upsert_application() ← Crear/actualizar candidatura
    ├── discard_offer()   ← Marcar oferta como descartada
    ├── get_offer()       ← Oferta por ID
    ├── get_offers_by_priority() ← Top N por priority
    ├── get_offers_by_date() ← Ofertas descubiertas en fecha
    ├── get_all_active_offers() ← Todas activas/applied
    ├── get_application_status() ← Candidatura + eventos
    ├── get_all_applications() ← Todas candidaturas (con filtro)
    ├── get_status_summary() ← Resumen agrupado por status
    └── search_offers()   ← Búsqueda textual
```

### 3.1 Patrón de uso desde el orquestador

```python
from scripts.db import insert_offer, get_offers_by_date, upsert_application

# Guardar evaluación
oid = insert_offer(company="Stripe", role="Senior BE", url="...",
                   tech_fit=85, career_fit=72, priority=82,
                   green_flags=8, red_flags=0, difficulty="Medium",
                   verdict="Apply", summary="...", platform="HN",
                   discovery_date="2026-07-11")

# Consultar ofertas del día
for o in get_offers_by_date("2026-07-11"):
    print(o["company"], o["priority"])

# Aplicar a una oferta
upsert_application(oid, "stripe", "in_progress")

# Consultar estado de candidatura
app = get_application_status("stripe")
```

---

## 4. Mapeo comando → DB

| Comando | Operación DB | Función db.py |
|---|---|---|
| `/search` / `/daily` | Insertar ofertas evaluadas | `insert_offer()` |
| `/search` / `/daily` | Registrar búsqueda | `insert_event()` |
| `/match <url>` | Insertar oferta evaluada | `insert_offer()` |
| `/apply <empresa>` | Crear/actualizar candidatura | `upsert_application()` |
| `/apply <empresa>` | Evento "applied" | `insert_event()` |
| `/cambiar-candidatura <estado>` | Actualizar candidatura | `upsert_application()` |
| `/cambiar-candidatura <estado>` | Evento cambio estado | `insert_event()` |
| `/estado-candidatura <empresa>` | Consultar candidatura + eventos | `get_application_status()` |
| `/lista-ofertas-diarias [fecha]` | Ofertas por fecha | `get_offers_by_date()` |
| `/lista-all-ofertas` | Todas las activas | `get_all_active_offers()` |
| `/descartar-oferta-diaria <emp>` | Marcar descartada | `discard_offer()` |
| `show-applied-jobs` (skill) | Candidaturas agrupadas | `get_all_applications()` + `get_status_summary()` |

---

## 5. Flujo de datos de un `/daily`

```
1. Diagnóstico de candidaturas
   └─ get_status_summary() + get_all_applications()

2. Búsqueda multi-plataforma
   └─ Himalayas, HN, RemoteOK, WWR, ATS (raw JSON en data/search/)

3. Evaluación dual (job-matcher)
   └─ Technical Fit + Career Fit → Priority Score

4. Cross-check con descartadas en DB
   └─ search_offers(company) → if discarded: preguntar

5. Persistencia en DB
   ├─ insert_offer() para cada oferta evaluada
   └─ insert_event("evaluated") para cada una

6. Log raw en data/search/YYYY-MM-DD/ (solo para debug)
```

---

## 6. Ficheros legacy (solo regeneración bajo demanda)

| Legacy | Regeneración |
|---|---|
| `data/jobs.csv` | `sqlite3 data/jobs.db ".mode csv" "SELECT * FROM offers" > data/jobs.csv` |
| `data/daily/YYYY-MM-DD.md` | Script ad-hoc (`scripts/generate-daily-log.py`) |
| `companies/<slug>/STATUS.md` | Script ad-hoc (`scripts/generate-status-md.py`) |

Estos ficheros **ya no se escriben** durante el flujo normal. Solo existen para compatibilidad visual o export.

---

## 7. Historial de migración

| Fase | Descripción | Fecha |
|---|---|---|
| 0.1 | Crear `db/schema.sql` (DDL completo) | 2026-07-11 |
| 0.2 | Crear `scripts/seed-db.py` (migración desde jobs.csv + STATUS.md) | 2026-07-11 |
| 0.3 | Crear `docker-compose.yml` + `data/metadata.json` (Datasette) | 2026-07-11 |
| 0.4 | Crear `scripts/db.py` (helper orquestador) | 2026-07-11 |
| 1 | Seed ejecutado: 27 offers, 9 applications, 39 events | 2026-07-11 |
| 2.1 | Adaptar `store-job` skill a DB | 2026-07-11 |
| 2.2 | Adaptar `show-applied-jobs` skill a DB | 2026-07-11 |
| 2.3 | Adaptar `daily` command a DB | 2026-07-11 |
| 2.4 | Adaptar `descartar-oferta-diaria` command a DB | 2026-07-11 |
| 2.5 | Adaptar `search`, `match`, `lista-ofertas-diarias`, `lista-all-ofertas`, `estado-candidatura`, `apply`, `cambiar-candidatura` a DB | 2026-07-11 |
| 2.6 | Adaptar `multi-platform-search` skill a DB | 2026-07-11 |
| 2.7 | Actualizar `AGENTS.md` con sección de persistencia | 2026-07-11 |

---

## 8. Exploración visual

```bash
# Con Docker (recomendado)
docker compose up -d     # Datasette en http://localhost:8001

# Sin Docker
pip install datasette && datasette data/jobs.db
```

La UI de Datasette permite explorar las 5 tablas, filtrar por columnas y exportar a CSV.
