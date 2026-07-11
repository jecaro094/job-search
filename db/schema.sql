-- db/schema.sql
-- Schema para la persistencia estructurada del sistema job-search
-- SQLite 3.x compatible

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
