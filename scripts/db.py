#!/usr/bin/env python3
"""
db.py — Helper de base de datos para el orquestador.
Proporciona funciones de lectura/escritura para jobs.db.

Uso desde el orquestador:
    from scripts.db import insert_offer, get_offers_by_priority, ...
"""
import hashlib, json, re, sqlite3
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path("data/jobs.db")

# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

def get_conn():
    """Devuelve una conexión a jobs.db (row_factory = Row)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def offer_id(company, role, url):
    """Hash determinista: misma oferta → mismo ID siempre."""
    raw = f"{company.lower().strip()}|{role.lower().strip()}|{(url or '').strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------

def insert_offer(company, role, url=None, tech_fit=None, career_fit=None,
                 priority=None, green_flags=0, red_flags=0, difficulty=None,
                 verdict=None, summary=None, source_platforms=None,
                 posting_date=None, discovery_date=None, platform=None):
    """Inserta o actualiza (upsert) una oferta. Retorna el offer_id."""
    conn = get_conn()
    try:
        oid = offer_id(company, role, url)
        slug = company.lower().replace(" ", "-")
        slug = re.sub(r"[^a-z0-9-]", "", slug)

        if discovery_date is None:
            discovery_date = str(date.today())

        conn.execute("""
            INSERT INTO offers
            (id, company, company_slug, role, url, platform,
             posting_date, discovery_date,
             tech_fit, career_fit, priority,
             green_flags, red_flags, difficulty, verdict,
             summary, source_platforms, status, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'active', datetime('now','+2 hours'))
            ON CONFLICT(id) DO UPDATE SET
                tech_fit = COALESCE(?, tech_fit),
                career_fit = COALESCE(?, career_fit),
                priority = COALESCE(?, priority),
                green_flags = COALESCE(?, green_flags),
                red_flags = COALESCE(?, red_flags),
                difficulty = COALESCE(?, difficulty),
                verdict = COALESCE(?, verdict),
                summary = COALESCE(?, summary),
                source_platforms = COALESCE(?, source_platforms),
                platform = COALESCE(?, platform),
                updated_at = datetime('now','+2 hours')
        """, (
            oid, company, slug, role, url, platform,
            posting_date, discovery_date,
            tech_fit, career_fit, priority,
            green_flags, red_flags, difficulty, verdict,
            summary, source_platforms,
            # valores para COALESCE en UPDATE
            tech_fit, career_fit, priority,
            green_flags, red_flags, difficulty, verdict,
            summary, source_platforms, platform,
        ))
        conn.commit()

        # Crear evento de evaluación
        if verdict:
            insert_event(oid, "evaluated", f"Priority {priority}/100 — {verdict}")

        return oid
    finally:
        conn.close()


def insert_event(offer_id, event_type, detail=None, metadata=None, event_date=None):
    """Inserta un evento en el timeline de una oferta."""
    conn = get_conn()
    try:
        if event_date is None:
            event_date = str(date.today())
        conn.execute("""
            INSERT INTO events (offer_id, event_date, event_type, detail, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (offer_id, event_date, event_type, detail,
              json.dumps(metadata) if metadata else None))
        conn.commit()
    finally:
        conn.close()


def upsert_application(offer_id, company_slug, status="in_progress",
                       source_platform=None, notes=None):
    """Inserta o actualiza el estado de una candidatura."""
    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO applications (offer_id, company_slug, status, source_platform, notes,
                                      created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, date('now','+2 hours'), datetime('now','+2 hours'))
            ON CONFLICT(offer_id) DO UPDATE SET
                status = ?,
                source_platform = COALESCE(?, source_platform),
                notes = COALESCE(?, notes),
                updated_at = datetime('now','+2 hours')
        """, (
            offer_id, company_slug, status, source_platform, notes,
            status, source_platform, notes,
        ))
        conn.commit()
    finally:
        conn.close()


def discard_offer(offer_id, reason=None):
    """Marca una oferta como descartada."""
    conn = get_conn()
    try:
        conn.execute("UPDATE offers SET status = 'discarded', updated_at = datetime('now','+2 hours') WHERE id = ?",
                     (offer_id,))
        insert_event(offer_id, "discarded", reason)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------

def get_offer(offer_id):
    """Devuelve una oferta por ID."""
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM offers WHERE id = ?", (offer_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_offers_by_priority(min_priority=None, status="active"):
    """Devuelve ofertas ordenadas por priority descendente.
    Si min_priority se especifica, filtra por priority >= min_priority.
    """
    conn = get_conn()
    try:
        if min_priority is not None:
            rows = conn.execute(
                "SELECT * FROM offers WHERE status = ? AND priority >= ? ORDER BY priority DESC",
                (status, min_priority)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM offers WHERE status = ? ORDER BY priority DESC",
                (status,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_offers_by_date(discovery_date, status=None):
    """Devuelve ofertas descubiertas en una fecha concreta (YYYY-MM-DD)."""
    conn = get_conn()
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM offers WHERE discovery_date = ? AND status = ? ORDER BY priority DESC",
                (discovery_date, status)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM offers WHERE discovery_date = ? ORDER BY priority DESC",
                (discovery_date,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_active_offers():
    """Devuelve todas las ofertas activas (no descartadas ni cerradas)."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM offers WHERE status IN ('active', 'applied') ORDER BY priority DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_application_status(company_slug):
    """Devuelve el estado completo de una candidatura (application + offer + events)."""
    conn = get_conn()
    try:
        row = conn.execute("""
            SELECT a.*, o.company, o.role, o.url, o.priority, o.verdict,
                   o.tech_fit, o.career_fit, o.difficulty, o.summary as offer_summary
            FROM applications a
            JOIN offers o ON o.id = a.offer_id
            WHERE a.company_slug = ?
            ORDER BY a.updated_at DESC
            LIMIT 1
        """, (company_slug,)).fetchone()
        if not row:
            return None

        result = dict(row)
        # Añadir eventos
        events = conn.execute(
            "SELECT * FROM events WHERE offer_id = ? ORDER BY event_date DESC",
            (result["offer_id"],)
        ).fetchall()
        result["events"] = [dict(e) for e in events]
        return result
    finally:
        conn.close()


def get_all_applications(status_filter=None):
    """Devuelve todas las candidaturas, opcionalmente filtradas por status."""
    conn = get_conn()
    try:
        query = """
            SELECT a.*, o.company, o.role, o.url, o.priority, o.verdict
            FROM applications a
            JOIN offers o ON o.id = a.offer_id
        """
        params = []
        if status_filter:
            query += " WHERE a.status = ?"
            params.append(status_filter)
        query += " ORDER BY a.updated_at DESC"

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_status_summary():
    """Devuelve resumen agrupado por status."""
    conn = get_conn()
    try:
        offers_by_status = conn.execute(
            "SELECT status, COUNT(*) as count FROM offers GROUP BY status"
        ).fetchall()

        apps_by_status = conn.execute(
            "SELECT status, COUNT(*) as count FROM applications GROUP BY status"
        ).fetchall()

        return {
            "offers": {r["status"]: r["count"] for r in offers_by_status},
            "applications": {r["status"]: r["count"] for r in apps_by_status},
        }
    finally:
        conn.close()


def search_offers(query):
    """Búsqueda textual simple por company o role."""
    conn = get_conn()
    try:
        like = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM offers WHERE company LIKE ? OR role LIKE ? ORDER BY priority DESC",
            (like, like)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
