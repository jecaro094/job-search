---
title: Persistencia SQLite + Docker
status: approved
author: orquestador
created: 2026-07-11
---

# SQLite como capa estructurada + Docker Datasette + Engram complementario

## Problema raíz

Actualmente abusamos de Engram guardando datos estructurados que no deberían estar ahí:

```
mem_save "Evaluada Kalepa Priority 99"     ← esto es una fila de BD, no memoria contextual
mem_save "Enveritas aplicada vía Greenhouse" ← igual
mem_save "Hack The Box descartada manualmente" ← igual
```

Engram está diseñado para **decisiones, patrones, descubrimientos**, no para ser un `INSERT INTO offers`. Cada vez que guardamos una evaluación en Engram, saturando su espacio con datos planos que además **no son consultables** (no puedo hacer `SELECT * FROM offers WHERE priority >= 85`).

## Schema propuesto

```sql
-- db/schema.sql

-- OFERTA: discovery + evaluación, ciclo de vida completo
CREATE TABLE IF NOT EXISTS offers (
  id TEXT PRIMARY KEY,              -- hash(company_slug + role + url)
  company TEXT NOT NULL,
  company_slug TEXT NOT NULL,
  role TEXT NOT NULL,
  url TEXT,
  platform TEXT,                    -- "Himalayas" o "HN, Greenhouse" (multi)
  posting_date DATE,
  discovery_date DATE NOT NULL,
  tech_fit INTEGER CHECK(tech_fit BETWEEN 0 AND 100),
  career_fit INTEGER CHECK(career_fit BETWEEN 0 AND 100),
  priority INTEGER CHECK(priority BETWEEN 0 AND 100),
  green_flags INTEGER DEFAULT 0,
  red_flags INTEGER DEFAULT 0,
  difficulty TEXT CHECK(difficulty IN ('Easy','Medium','Hard')),
  verdict TEXT CHECK(verdict IN ('Apply immediately','Apply','Consider','Skip')),
  summary TEXT,
  source_platforms TEXT,
  status TEXT DEFAULT 'active' CHECK(status IN ('active','expired','discarded','applied','closed')),
  created_at DATETIME DEFAULT (datetime('now','+2 hours')),  -- CET
  updated_at DATETIME DEFAULT (datetime('now','+2 hours'))
);

-- TIMELINE: cada evento en la vida de una oferta
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id TEXT NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
  event_date DATE NOT NULL DEFAULT (date('now','+2 hours')),
  event_type TEXT NOT NULL CHECK(event_type IN (
    'discovered','evaluated','re-evaluated','applied','interview_scheduled',
    'interview_done','rejected','accepted','discarded','expired','manual_note'
  )),
  detail TEXT,
  metadata TEXT,                    -- JSON: {"stage":2,"interviewer":"Elena"}
  created_at DATETIME DEFAULT (datetime('now','+2 hours'))
);

-- CANDIDATURA: lo que hoy es STATUS.md
CREATE TABLE IF NOT EXISTS applications (
  offer_id TEXT PRIMARY KEY REFERENCES offers(id) ON DELETE CASCADE,
  company_slug TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'in_progress' CHECK(status IN (
    'hot','in_progress','limbo','descartado'
  )),
  source_platform TEXT,
  cv_version TEXT,
  notes TEXT,
  created_at DATE NOT NULL DEFAULT (date('now','+2 hours')),
  updated_at DATETIME DEFAULT (datetime('now','+2 hours'))
);

-- RONDA DE BÚSQUEDA: métricas de cada ejecución
CREATE TABLE IF NOT EXISTS search_rounds (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  search_date DATE NOT NULL DEFAULT (date('now','+2 hours')),
  search_time TIME NOT NULL DEFAULT (time('now','+2 hours')),
  platform TEXT NOT NULL,
  offers_scanned INTEGER DEFAULT 0,
  offers_passed INTEGER DEFAULT 0,
  offers_evaluated INTEGER DEFAULT 0,
  duration_seconds INTEGER
);

-- APRENDIZAJES: lo que SÍ debería ir a memoria contextual
-- (se sincroniza con Engram, pero además persiste en DB para no perderlo)
CREATE TABLE IF NOT EXISTS learnings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date DATE NOT NULL DEFAULT (date('now','+2 hours')),
  category TEXT CHECK(category IN (
    'discovery','decision','pattern','gotcha','preference'
  )),
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  synced_to_engram INTEGER DEFAULT 0
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_offers_status ON offers(status);
CREATE INDEX IF NOT EXISTS idx_offers_priority ON offers(priority DESC);
CREATE INDEX IF NOT EXISTS idx_offers_company ON offers(company_slug);
CREATE INDEX IF NOT EXISTS idx_offers_discovery ON offers(discovery_date DESC);
CREATE INDEX IF NOT EXISTS idx_events_offer ON events(offer_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_search_rounds_date ON search_rounds(search_date DESC);

-- Vista: ofertas activas con su última aplicación
CREATE VIEW IF NOT EXISTS active_offers AS
  SELECT o.id, o.company, o.role, o.priority, o.verdict, o.status,
         a.status as application_status,
         (SELECT event_type FROM events e WHERE e.offer_id = o.id ORDER BY e.event_date DESC LIMIT 1) as last_event
  FROM offers o
  LEFT JOIN applications a ON a.offer_id = o.id
  WHERE o.status IN ('active', 'applied');
```

**Clave del diseño**: `offers.id` = hash determinista (SHA256 de `company_slug + "|" + role + "|" + url`). Si la misma oferta aparece en dos rondas de búsqueda, el hash es idéntico → **upsert** en lugar de duplicado.

## Docker Compose

Servicio **Datasette** — visor web + API REST para la SQLite:

```yaml
version: '3.8'

services:
  datasette:
    image: datasette/datasette:latest
    container_name: job-search-db
    ports:
      - "8001:8001"
    volumes:
      - ./data:/data
    command: >
      datasette -p 8001 -h 0.0.0.0
      /data/jobs.db
      --metadata /data/metadata.json
      --setting allow_download on
      --setting sql_time_limit_ms 5000
      --setting max_returned_rows 2000
    restart: "no"
    # restart: unless-stopped   ← DESCOMENTAR para producción
```

Fichero `data/metadata.json` (para mejorar la UI de Datasette):

```json
{
  "title": "job-search DB",
  "description": "Ofertas, aplicaciones y eventos del sistema job-search",
  "databases": {
    "jobs": {
      "tables": {
        "offers": {
          "sort": "priority",
          "sort_desc": true
        },
        "events": {
          "sort": "event_date",
          "sort_desc": true
        },
        "applications": {
          "sort": "updated_at",
          "sort_desc": true
        }
      }
    }
  }
}
```

## Reparto: SQLite vs Engram

| Tipo de dato | ¿Dónde va? | Ejemplo |
|---|---|---|
| Evaluación, score, plataforma | **SQLite** → `offers` | `Kalepa, Priority 99, Himalayas` |
| Timeline de eventos | **SQLite** → `events` | `2026-07-11: applied, 2026-07-11: re-evaluated` |
| Estado de candidatura | **SQLite** → `applications` | `enveritas, in_progress, applied vía Greenhouse` |
| Decisión sobre scoring | **Engram** → `decision` | "Re-scored Kalepa 91→99 tras confirmar Python" |
| Patrón descubierto | **Engram** → `discovery` | "Ashby devuelve ofertas >60d sin avisar" |
| Preferencia del usuario | **Engram** → `preference` | "No aplicar a non-profits" (si aplica) |
| Filtro aprendido | **Engram** → `pattern` | "Consultoras con dominio financiero → -20" |

**Regla**: SQLite guarda el **qué** (hechos). Engram guarda el **por qué** (contexto, decisión, gotcha). Si puedes responder con `SELECT`, no lo guardes en Engram.

## Fases de ejecución

### Fase 0 — Preparación (~15 min)

| # | Acción | Archivos | Qué produce |
|---|--------|----------|-------------|
| 0.1 | Crear schema SQLite | `db/schema.sql` | DDL de tablas |
| 0.2 | Crear seed script | `scripts/seed-db.py` | Lee `jobs.csv` + `companies/*/STATUS.md` → `jobs.db` |
| 0.3 | Crear docker-compose | `docker-compose.yml` | Datasette + volumen |
| 0.4 | Crear metadata | `data/metadata.json` | Mejora UI Datasette |

**Criterio de éxito**: `python scripts/seed-db.py` corre sin errores y `data/jobs.db` existe con datos.

### Fase 1 — Hito: Seed + Datasette visible

| # | Acción | Depende de |
|---|--------|------------|
| 1.1 | Ejecutar seed | 0.1 + 0.2 |
| 1.2 | `docker compose up -d` | 0.3 + 1.1 |
| 1.3 | Verificar `http://localhost:8001` muestra tablas con datos | 1.2 |
| 1.4 | Commit: `db/schema.sql`, `scripts/seed-db.py`, `docker-compose.yml`, `data/metadata.json` | 1.3 |

**Criterio de éxito**: Abro navegador, veo tabla `offers` con 14 evaluaciones.

### ⚠️ Principio rector: leer desde DB desde el día 1 del dual write

Durante el dual write, **todas las lecturas van contra SQLite**, no contra los ficheros legacy. Los ficheros solo se escriben (por seguridad) pero nunca se leen para responder consultas.

Esto aplica a:

| Comando / función | Antes (lee fichero) | Después (lee DB) |
|---|---|---|
| `/lista-ofertas-diarias` | `data/daily/YYYY-MM-DD.md` | `SELECT * FROM offers WHERE discovery_date = '...' ORDER BY priority DESC` |
| `/lista-all-ofertas` | Múltiples `.md` + `jobs.csv` | `SELECT * FROM offers WHERE status IN ('active','applied')` |
| `/estado-candidatura <empresa>` | `companies/<slug>/STATUS.md` | `SELECT * FROM applications JOIN offers JOIN events WHERE company_slug = '...'` |
| `show-applied-jobs` skill | `companies/*/STATUS.md` | `SELECT * FROM applications WHERE status IN ('hot','in_progress','limbo')` |
| Consolidación de logs | Parseo manual de .md | `SELECT * FROM offers WHERE ...` + se genera el .md como vista |
| Diagnóstico de companies | `companies/*/STATUS.md` | `SELECT status, COUNT(*) FROM applications GROUP BY status` |

**¿Por qué tiene sentido?**

1. **Validación continua**: si la DB responde distinto que los ficheros, hay un bug que se detecta al instante
2. **Un solo camino de lectura**: no hay que mantener dos parseadores (uno para `.md`, otro para DB)
3. **Cutover trivial**: cuando se dejen de escribir ficheros, nada cambia en las lecturas — ya leen de DB
4. **Rendimiento**: SQLite indexado responde en milisegundos. Grepear 1.200 líneas de `.md` no

### Fase 2 — Migración inmediata (seed + cutover, sin dual write)

> Según decisión del usuario: **migración inmediata**. No hay período de dual write. Una vez creada la DB, el orquestador escribe y lee solo de SQLite. Los ficheros legacy (jobs.csv, daily logs, STATUS.md) pasan a ser **vistas generadas** bajo demanda desde la DB.

| # | Acción | Archivos a modificar | Qué cambia |
|---|--------|----------------------|------------|
| 2.1 | Crear helper `db.py` | `scripts/db.py` | Funciones: `insert_offer()`, `insert_event()`, `upsert_application()`, `get_offers_by_priority()`, `get_offers_by_date()`, `get_application_status()` |
| 2.2 | Adaptar `store-job` skill | `.opencode/skills/store-job/SKILL.md` | En lugar de escribir CSV, llama a `insert_offer()`. CSV se genera como export opcional |
| 2.3 | Adaptar `/apply` | Orquestador | `insert_event("applied")` + `upsert_application("in_progress")`. Deja de escribir STATUS.md |
| 2.4 | Adaptar `/descartar-oferta-diaria` | Orquestador | `UPDATE offers SET status='discarded'` + `insert_event("discarded")` |
| 2.5 | Migrar `/lista-ofertas-diarias` | Orquestador | En lugar de parsear `.md`, ejecuta `get_offers_by_date(fecha)` y genera tabla desde DB |
| 2.6 | Migrar `/lista-all-ofertas` | Orquestador | `SELECT * FROM offers WHERE status IN ('active','applied') ORDER BY priority DESC` |
| 2.7 | Migrar `/estado-candidatura` | Orquestador | `SELECT * FROM applications JOIN offers JOIN events WHERE company_slug = ?` |
| 2.8 | Migrar `show-applied-jobs` skill | `.opencode/skills/show-applied-jobs/SKILL.md` | Lee de DB en lugar de `companies/*/STATUS.md` |

**Criterio de éxito**: Todos los comandos de consulta responden desde SQLite. No se escribe ni un `.md` ni `.csv` nuevo durante una `/daily`.

### Fase 3 — Consolidación de nombres (durante seed)

| # | Acción | Qué resuelve |
|---|--------|-------------|
| 3.1 | Normalizar slugs inconsistentes en el seed | `canonical-python` + `canonical-senior` → unificar a `canonical`. Mapear slugs de companies/ a company_slug normalizado. Detectar duplicados y fusionar. |

**Integrado en seed**: el script `seed-db.py` aplica el mapping de slugs durante la migración inicial, no después.

### Fase 4 — Post-migración

> ⚡ **Como no hay dual write, el cutover ya ocurrió en Fase 2. Esta fase solo verifica que el sistema legacy puede regenerarse desde DB si se necesita.**

| # | Acción | Qué se verifica |
|---|--------|-----------------|
| 4.1 | jobs.csv desde DB | `sqlite3 data/jobs.db ".mode csv" "SELECT * FROM offers" > data/jobs.csv` contiene exactamente las mismas filas que el original |
| 4.2 | Log diario desde DB | `scripts/generate-daily-log.py 2026-07-11` produce el mismo contenido que `data/daily/2026-07-11.md` |
| 4.3 | STATUS.md desde DB | `scripts/generate-status-md.py <slug>` produce el mismo contenido que `companies/<slug>/STATUS.md` |
| 4.4 | RAW JSON | Se conserva como debug opcional. Sin cambios. |

**Criterio de éxito**: Todos los ficheros legacy se regeneran idénticos desde la DB.

### Fase 5 — Optimización de memoria Engram

| # | Acción | Qué se deja de guardar en Engram |
|---|--------|----------------------------------|
| 5.1 | Identificar saves obsoletos | `mem_search "evaluated"` → encontrar evaluaciones guardadas como memoria |
| 5.2 | Marcar como obsoletos | Esos saves ya no se necesitan: los datos están en SQLite |
| 5.3 | A partir de ahora | Engram solo guarda decisiones de scoring, patrones descubiertos, preferencias, gotchas |

**Criterio de éxito**: Engram se usa para contexto, no como base de datos.

## Seed script: estructura

```python
#!/usr/bin/env python3
"""
Seed: lee jobs.csv + companies/*/STATUS.md → jobs.db
Uso: python scripts/seed-db.py
"""
import csv, hashlib, json, os, sqlite3, re
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path("data/jobs.db")
CSV_PATH = Path("data/jobs.csv")
COMPANIES_DIR = Path("companies")

def offer_id(company, role, url):
    """Hash determinista: misma oferta → mismo ID siempre"""
    raw = f"{company.lower().strip()}|{role.lower().strip()}|{(url or '').strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def seed():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(open("db/schema.sql").read())

    # 1. Leer jobs.csv → INSERT offers
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            oid = offer_id(row["company"], row["title"], row.get("url",""))
            conn.execute("""
                INSERT OR REPLACE INTO offers
                (id, company, role, url, tech_fit, career_fit, priority,
                 green_flags, red_flags, difficulty, verdict, summary,
                 source_platforms, discovery_date, status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'active')
            """, (
                oid, row["company"], row["title"], row.get("url"),
                row.get("technical_fit"), row.get("career_fit"),
                row.get("priority_score"), row.get("green_flags"),
                row.get("red_flags"), row.get("difficulty"),
                row.get("verdict"), row.get("summary"),
                row.get("source_platforms"), row.get("date", str(date.today()))
            ))

    # 2. Leer companies/*/STATUS.md → INSERT applications + events
    for status_path in COMPANIES_DIR.glob("*/STATUS.md"):
        slug = status_path.parent.name
        content = status_path.read_text()

        # Extraer campos con regex simples
        name_match = re.search(r"^# (.+?)(?: — |$)", content, re.M)
        status_match = re.search(r"\*\*Status\*\*:\s*(.+)", content)

        company_name = name_match.group(1) if name_match else slug
        company_status = status_match.group(1).strip() if status_match else "in_progress"

        # Convertir status al enum
        status_map = {
            "🟢 Hot": "hot", "Hot": "hot",
            "🟡 In progress": "in_progress", "In progress": "in_progress",
            "⚪ En el limbo": "limbo", "En el limbo": "limbo",
            "🔴 Descartado": "descartado", "Descartado": "descartado",
        }
        status_val = status_map.get(company_status, "in_progress")

        # Buscar events en timeline
        in_timeline = False
        for line in content.split("\n"):
            if "| Date | Event |" in line:
                in_timeline = True
                continue
            if in_timeline and line.startswith("|---"):
                continue
            if in_timeline and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 2 and parts[0] and parts[1]:
                    # insertar evento (simplificado, se completa en implementación)
                    pass

    conn.commit()
    conn.close()
    print(f"✅ Seed completado: {DB_PATH}")

if __name__ == "__main__":
    seed()
```

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Dependencia de SQLite (un fichero) | Backup automático: `cp data/jobs.db data/backups/jobs-$(date +%F).db` |
| Complejidad añadida | El seed script + dual write son transitorios. Se puede revertir borrando `jobs.db` |
| Docker no disponible | Datasette funciona sin Docker: `pip install datasette && datasette data/jobs.db` |
| Pérdida de edición manual de .md | Los .md se convierten en **vistas generadas**, no fuente de verdad. Si editas a mano, hay que sincronizar |

## Artefactos a crear

```
job-search/
├── db/
│   └── schema.sql                    ← DDL completo
├── scripts/
│   ├── seed-db.py                    ← Migración inicial
│   ├── db.py                         ← Helper Python para el orquestador
│   └── query-db.sh                   ← Wrapper sqlite3 para consultas rápidas
├── docker-compose.yml                ← Datasette + volumen
├── data/
│   ├── metadata.json                 ← Config UI Datasette
│   └── jobs.db                       ← Generado por seed-db.py (gitignored)
└── .gitignore
    └── + data/jobs.db                ← No versionar la BD (solo schema)
```

## Preguntas pendientes para el usuario

1. **¿Mantener logs `.md` como fuente de verdad humana** (editables a mano) **o vale que se generen desde la DB?**
  - si lo simplifica, basate en la base de datos para cualquier operacion / comando / skill del agente que lo requiera.
2. **¿Migración inmediata** (seed + corte) **o gradual** (dual write 1 semana)?
  - migracion inmediata
3. **¿Docker compose para producción** (siempre corriendo) **o solo consulta bajo demanda?**
  - solo consulta y se lanza bajo demanda
4. **¿Unificar nombres de empresa** (casos como `canonical-python` vs `canonical-senior`) **durante la migración?**
  - si
