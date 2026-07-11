#!/usr/bin/env python3
"""
seed-db.py — Migración inicial: lee jobs.csv + companies/*/STATUS.md → jobs.db
Uso: python scripts/seed-db.py [--force]

Normaliza slugs: canonical-python, canonical-senior → canonical
                  bark-com → bark, etc.
"""
import csv, hashlib, re, sqlite3, sys
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path("data/jobs.db")
CSV_PATH = Path("data/jobs.csv")
COMPANIES_DIR = Path("companies")

# Mapping de normalización de slugs (company_slug → nombre canónico)
# Resuelve: canonical-python + canonical-senior → canonical
#           bark-com → bark, etc.
SLUG_NORMALIZE = {
    "canonical-python": "canonical",
    "canonical-senior": "canonical",
    "bark-com": "bark",
    "fever-senior-engineer": "fever",
    "fever-home-office": "fever",
    "fever-tech-lead": "fever",
    "hays-hostpapa": "hays",
    "hostpapa-cloudblue": "hostpapa",
    "eurobase-healthcare-ai": "eurobase",
    "eurobase-people": "eurobase",
    "digital-skills-ldt": "digital-skills-ldt",
    "profile-software-services": "profile-software",
    "sdg-group": "sdg-group",
    "spd-technology": "spd-technology",
    "treelogy-tech": "treelogy",
    "veeva-systems": "veeva-systems",
    "z1-digital": "z1-digital",
    "remote-com": "remote-com",
    "hired": "hired",
    "novakid-school": "novakid-school",
    "law-business-research": "law-business-research",
    "icloudcompliance": "icloud-compliance",
}

# Reverse mapping: nombre canónico → slugs a fusionar
def get_canonical_slug(slug):
    """Devuelve el slug canónico para un slug dado."""
    return SLUG_NORMALIZE.get(slug, slug)

def get_company_slugs_for_canonical(canonical):
    """Devuelve todos los slugs que mapean a un canónico."""
    if canonical not in SLUG_NORMALIZE.values():
        return {canonical}
    slugs = {canonical}
    for k, v in SLUG_NORMALIZE.items():
        if v == canonical:
            slugs.add(k)
    return slugs


def offer_id(company, role, url):
    """Hash determinista: misma oferta → mismo ID siempre."""
    raw = f"{company.lower().strip()}|{role.lower().strip()}|{(url or '').strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def parse_status_from_md(content):
    """Extrae status de un STATUS.md. Retorna el valor normalizado."""
    m = re.search(r"\*\*Status\*\*:\s*(.+)", content)
    if not m:
        return "in_progress"
    raw = m.group(1).strip()
    mapping = {
        "🟢 Hot": "hot", "Hot": "hot",
        "🟡 In progress": "in_progress", "In progress": "in_progress",
        "⚪ En el limbo": "limbo", "En el limbo": "limbo",
        "🔴 Descartado": "descartado", "Descartado": "descartado",
    }
    return mapping.get(raw, "in_progress")


def parse_platform_from_md(content):
    """Extrae source platform de un STATUS.md."""
    m = re.search(r"\*\*Source platform\*\*:\s*(.+)", content)
    return m.group(1).strip() if m else None


def parse_company_name_from_md(content):
    """Extrae el nombre de empresa del H1 del STATUS.md."""
    m = re.search(r"^# (.+?)(?: — |$)", content, re.MULTILINE)
    return m.group(1).strip() if m else None


def parse_role_from_md(content):
    """Extrae el rol de un STATUS.md (si tiene campo Role)."""
    m = re.search(r"\*\*Role\*\*:\s*(.+)", content)
    return m.group(1).strip() if m else None


def parse_timeline_events(content, slug):
    """Parsea la tabla Timeline de un STATUS.md y devuelve lista de eventos."""
    events = []
    in_timeline = False
    for line in content.split("\n"):
        if "| Date | Event |" in line:
            in_timeline = True
            continue
        if in_timeline and line.strip().startswith("|---"):
            continue
        if in_timeline and line.strip().startswith("|"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 2 and parts[0] and parts[1]:
                event_date = parts[0]
                event_detail = parts[1]
                # Determinar event_type por el contenido
                event_type = "manual_note"
                if "evaluada" in event_detail.lower() or "scoring" in event_detail.lower() or "priority" in event_detail.lower():
                    event_type = "evaluated"
                elif "aplicada" in event_detail.lower() or "applied" in event_detail.lower() or "cv enviado" in event_detail.lower() or "candidatura" in event_detail.lower():
                    event_type = "applied"
                elif "stage" in event_detail.lower() or "entrevista" in event_detail.lower() or "interview" in event_detail.lower() or "recruiter" in event_detail.lower() or "technical screen" in event_detail.lower():
                    event_type = "interview_done"
                elif "descartad" in event_detail.lower() or "rechazad" in event_detail.lower() or "rejected" in event_detail.lower():
                    event_type = "rejected"
                elif "importado" in event_detail.lower() or "imported" in event_detail.lower() or "added to" in event_detail.lower():
                    event_type = "discovered"

                events.append({
                    "date": event_date,
                    "type": event_type,
                    "detail": event_detail,
                })
    return events


def seed():
    force = "--force" in sys.argv

    if DB_PATH.exists() and not force:
        print(f"⚠️  {DB_PATH} ya existe. Usa --force para sobreescribir.")
        sys.exit(1)

    # Conectar y crear schema
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(open("db/schema.sql").read())

    stats = {"offers": 0, "events": 0, "applications": 0, "search_rounds": 0, "learnings": 0, "errors": 0}

    # ================================================================
    # 1. Leer jobs.csv → INSERT offers
    # ================================================================
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    company = row.get("company", "").strip()
                    title = row.get("title", "").strip()
                    url = row.get("url", "").strip()
                    oid = offer_id(company, title, url)

                    # Normalizar company_slug
                    raw_slug = company.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")
                    raw_slug = re.sub(r"[^a-z0-9-]", "", raw_slug)
                    company_slug = get_canonical_slug(raw_slug)

                    tech_fit = row.get("technical_fit", "")
                    career_fit = row.get("career_fit", "")
                    priority = row.get("priority_score", "")
                    green = row.get("green_flags", "0")
                    red = row.get("red_flags", "0")
                    difficulty = row.get("difficulty", "")
                    verdict = row.get("verdict", "")
                    summary = row.get("summary", "")
                    source = row.get("source_platforms", "")
                    disc_date = row.get("date", str(date.today()))

                    # Parsear valores numéricos
                    def to_int(v, default=None):
                        try:
                            return int(float(v))
                        except (ValueError, TypeError):
                            return default

                    # Normalizar difficulty
                    norm_difficulty = None
                    if difficulty:
                        d = difficulty.strip().lower()
                        if d in ("easy", "🟢 easy"):
                            norm_difficulty = "Easy"
                        elif d in ("medium", "🟡 medium", "🟡 medium)"):
                            norm_difficulty = "Medium"
                        elif d in ("hard", "🔴 hard"):
                            norm_difficulty = "Hard"

                    # Normalizar verdict
                    norm_verdict = None
                    if verdict:
                        v = verdict.strip()
                        if v.startswith("Apply immediately"):
                            norm_verdict = "Apply immediately"
                        elif v == "Apply":
                            norm_verdict = "Apply"
                        elif v.startswith("Consider"):
                            norm_verdict = "Consider"
                        elif v in ("Skip", "Rejected", "❌ Skip"):
                            norm_verdict = "Skip"

                    conn.execute("""
                        INSERT OR REPLACE INTO offers
                        (id, company, company_slug, role, url, tech_fit, career_fit, priority,
                         green_flags, red_flags, difficulty, verdict, summary,
                         source_platforms, discovery_date, posting_date, status)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'active')
                    """, (
                        oid, company, company_slug, title,
                        url if url and url != "N/A" else None,
                        to_int(tech_fit), to_int(career_fit), to_int(priority),
                        to_int(green, 0), to_int(red, 0),
                        norm_difficulty,
                        norm_verdict,
                        summary if summary else None,
                        source if source else None,
                        disc_date,
                        None,  # posting_date no disponible en CSV
                    ))
                    stats["offers"] += 1

                    # Crear evento de evaluación
                    if verdict:
                        conn.execute("""
                            INSERT INTO events (offer_id, event_date, event_type, detail)
                            VALUES (?, ?, 'evaluated', ?)
                        """, (oid, disc_date, f"Priority {priority}/100 — {verdict}"))
                        stats["events"] += 1

                except Exception as e:
                    print(f"  ❌ Error procesando fila de CSV: {e}")
                    stats["errors"] += 1

        print(f"  📥 {stats['offers']} offers desde jobs.csv")
    else:
        print(f"  ⚠️  {CSV_PATH} no encontrado. No se cargaron ofertas desde CSV.")

    # ================================================================
    # 2. Leer companies/*/STATUS.md → INSERT applications + events
    # ================================================================
    for status_path in sorted(COMPANIES_DIR.glob("*/STATUS.md")):
        slug = status_path.parent.name
        content = status_path.read_text()
        canonical_slug = get_canonical_slug(slug)
        company_name = parse_company_name_from_md(content) or slug
        status_val = parse_status_from_md(content)
        platform = parse_platform_from_md(content)
        role = parse_role_from_md(content)
        events = parse_timeline_events(content, slug)

        try:
            # Buscar offer_id existente para esta empresa
            existing_offers = conn.execute(
                "SELECT id FROM offers WHERE company_slug = ? ORDER BY created_at DESC LIMIT 1",
                (canonical_slug,)
            ).fetchone()

            offer_id_val = existing_offers["id"] if existing_offers else None

            if offer_id_val:
                # Insert o actualizar application
                conn.execute("""
                    INSERT OR REPLACE INTO applications
                    (offer_id, company_slug, status, source_platform, notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, date('now','+2 hours'), datetime('now','+2 hours'))
                """, (
                    offer_id_val, canonical_slug, status_val,
                    platform,
                    f"Company: {company_name}" + (f"\nRole: {role}" if role else "")
                ))
                stats["applications"] += 1

                # Insertar eventos del timeline
                for ev in events:
                    # Evitar duplicar el evento evaluated si ya existe desde CSV
                    if ev["type"] == "evaluated":
                        existing = conn.execute(
                            "SELECT id FROM events WHERE offer_id = ? AND event_type = 'evaluated' AND event_date = ?",
                            (offer_id_val, ev["date"])
                        ).fetchone()
                        if existing:
                            continue
                    conn.execute("""
                        INSERT INTO events (offer_id, event_date, event_type, detail)
                        VALUES (?, ?, ?, ?)
                    """, (offer_id_val, ev["date"], ev["type"], ev["detail"]))
                    stats["events"] += 1

        except Exception as e:
            print(f"  ❌ Error procesando {slug}: {e}")
            stats["errors"] += 1

    print(f"  📥 {stats['applications']} applications desde STATUS.md")
    print(f"  📥 {stats['events']} events totales")

    # ================================================================
    # 3. Actualizar status de offers según applications
    # ================================================================
    conn.execute("""
        UPDATE offers SET status = 'applied'
        WHERE id IN (SELECT offer_id FROM applications WHERE status IN ('hot', 'in_progress'))
    """)
    conn.execute("""
        UPDATE offers SET status = 'discarded'
        WHERE id IN (SELECT offer_id FROM applications WHERE status = 'descartado')
    """)

    conn.commit()
    conn.close()

    # ================================================================
    # Resumen
    # ================================================================
    print(f"\n✅ Seed completado: {DB_PATH}")
    print(f"   Offers: {stats['offers']}")
    print(f"   Applications: {stats['applications']}")
    print(f"   Events: {stats['events']}")
    print(f"   Errors: {stats['errors']}")
    print(f"\n   Volcado rápido: sqlite3 {DB_PATH} \"SELECT COUNT(*) as offers, "
          f"(SELECT COUNT(*) FROM applications) as apps, "
          f"(SELECT COUNT(*) FROM events) as events\"")
    print(f"   UI: datasette {DB_PATH}  (o docker compose up -d)")


if __name__ == "__main__":
    seed()
