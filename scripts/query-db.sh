#!/bin/bash
# query-db.sh — Wrapper rápido para consultar data/jobs.db
# Uso: ./scripts/query-db.sh "SELECT * FROM offers LIMIT 5"
#      ./scripts/query-db.sh "SELECT status, COUNT(*) FROM offers GROUP BY status"

DB="data/jobs.db"

if [ ! -f "$DB" ]; then
    echo "❌ $DB no encontrado. Ejecuta 'python scripts/seed-db.py --force' primero."
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Uso: $0 <consulta SQL>"
    echo ""
    echo "Consultas útiles:"
    echo "  $0 \"SELECT * FROM offers WHERE status='active' ORDER BY priority DESC\""
    echo "  $0 \"SELECT * FROM applications WHERE status='in_progress'\""
    echo "  $0 \"SELECT event_type, COUNT(*) FROM events GROUP BY event_type\""
    echo "  $0 \"SELECT * FROM offers WHERE company LIKE '%enveritas%'\""
    exit 1
fi

sqlite3 -header -column "$DB" "$1"
