# Feature: LinkedIn Playwright Scraper

## Status: ✅ Approved and implemented

> Decisiones del usuario (2026-07-10):
> - Login: Opción A (cookies persistentes, login manual 1 vez) ✅
> - Frecuencia: Máximo 2 búsquedas/día. Si intenta más → bloqueo explícito con mensaje
> - Modo: Headless + fingerprint spoofing ✅
> - Playwright: Vía `npm install playwright` (local, no global) + npx para browsers ✅

## Problem

LinkedIn via `websearch` (Composio/Exa) devuelve ~10-15% de las ofertas reales: solo las indexadas por buscadores, normalmente con 1-7 días de retraso, sin filtros reales de ubicación/remoto, y sesgadas hacia US/LATAM/Asia.

## Solution

Reemplazar `COMPOSIO_SEARCH_WEB` + `COMPOSIO_SEARCH_FETCH_URL_CONTENT` por un script Node.js con Playwright que accede directamente a LinkedIn Jobs usando una sesión real del usuario.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                orquestador (openagent)                    │
│  • Ejecuta el scraper script directamente                │
│  • Lee el JSON de salida y pasa a job-matcher            │
└───────────────────────┬─────────────────────────────────┘
                        │ exec
┌───────────────────────▼─────────────────────────────────┐
│          scripts/linkedin-scraper.mjs (Node.js)          │
│  • Playwright con sesión real de LinkedIn                 │
│  • Anti-detección: fingerprint, delays, headers           │
│  • 3 queries paralelas por ejecución                      │
│  • Salida: JSON en data/search/YYYY-MM-DD/HH-MM-*.json   │
└───────────────────────┬─────────────────────────────────┘
                        │ reads
┌───────────────────────▼─────────────────────────────────┐
│         .linkedin-cookies/auth-cookies.json               │
│  • Cookies de sesión guardadas tras login manual          │
│  • Rotan cada ~30 días, script avisa si expiran           │
└─────────────────────────────────────────────────────────┘
```

## Anti-detection strategy

### 1. Fingerprint spoofing
- `userAgent` → cadena real de Chrome 125+ en macOS
- `viewport` → aleatorio entre 1280x800 y 1920x1080
- `locale` → `en-US` (LinkedIn global)
- `timezone` → `Europe/Madrid`
- `geolocation` → desactivado
- `navigator.webdriver` → forzado a `false` via CDP
- `navigator.languages` → `['en-US', 'en', 'es']`
- WebGL vendor → `Google Inc. (Apple)`
- Canvas fingerprint → aleatorio por sesión
- `--disable-blink-features=AutomationControlled`

### 2. Behavioral
- Delays aleatorios entre acciones: 2-5s (movimiento), 3-8s (scroll)
- Scroll gradual simulando lectura humana (no instantáneo)
- Click con coordenadas reales (no center-center)
- Máximo 3 queries por ejecución (no 8 como ahora)

### 3. Session management
- Cookies guardadas en `.linkedin-cookies/auth-cookies.json`
- Si cookies expiran → abortar con mensaje claro: "🔴 Sesión expirada. Ejecuta: node scripts/linkedin-scraper.mjs --login"
- Modo `--login`: abre navegador **headed**, tú haces login manual, guarda cookies
- Modo normal (sin flag): **headless** con cookies guardadas

### 4. Rate limiting
- **Máximo 2 ejecuciones/día** — hard limit. Si el usuario intenta más, el skill lo bloquea con mensaje explícito: "🔴 Límite diario alcanzado (2/2). Vuelve mañana o usa `/search` para otras plataformas."
- Mínimo 6h entre ejecuciones
- Queries secuenciales (no paralelas) para evitar detección. ~5-8s por query + delays humanos entre ellas
- Tiempo total estimado por ejecución: 3-5 minutos
- El límite se trackea en `data/.linkedin-rate-limit.json` con últimas 2 fechas

## Script interface

```bash
# Login (headed, manual)
node scripts/linkedin-scraper.mjs --login

# Search (headless, usa cookies si existen)
node scripts/linkedin-scraper.mjs

# Search with custom queries
node scripts/linkedin-scraper.mjs --queries "python backend senior" "python data engineer"

# Force headed mode
node scripts/linkedin-scraper.mjs --headed
```

## Output format

Cada ejecución genera:
- `data/search/YYYY-MM-DD/HH-MM-linkedin-playwright.json` — resultados completos

```json
{
  "channel": "linkedin-playwright",
  "date": "2026-07-10",
  "time": "14:30",
  "session_valid": true,
  "queries_executed": 3,
  "total_listings": 25,
  "results": [
    {
      "title": "Senior Backend Engineer",
      "company": "Example Corp",
      "location": "Madrid, Spain",
      "remote_policy": "Remote",
      "url": "https://www.linkedin.com/jobs/view/1234567890/",
      "post_date": "2026-07-09",
      "description_snippet": "...",
      "description_full_url": "https://www.linkedin.com/jobs/view/1234567890/"
    }
  ],
  "errors": [],
  "timing_ms": 45000
}
```

## Queries

3 queries verticales por ejecución (máximo), rotando entre:

| # | Query | LinkedIn filters |
|---|-------|-----------------|
| 1 | `python backend senior remote` | Geo: Europe, Date: Past 24h, Remote: Yes |
| 2 | `python data engineer remote` | Geo: Europe, Date: Past 24h, Remote: Yes |
| 3 | `python api developer remote` | Geo: Europe, Date: Past week, Remote: Yes |

> En futuras ejecuciones, rotar queries para cubrir más verticales sin repetir exactamente las mismas.

## Pipeline integration

El flujo de LinkedIn (optativo, preguntar siempre) funciona así:

1. El orquestador pregunta: "¿Quieres buscar también en LinkedIn?"
2. Si el usuario acepta, se verifica si el script existe en `scripts/linkedin-scraper.mjs`
3. Verificar si hay cookies válidas en `.linkedin-cookies/auth-cookies.json`
4. Si no → pedir al usuario que ejecute `--login`
5. Si sí → ejecutar script, esperar JSON
6. Leer JSON, procesar resultados (filtros, cross-check, job-matcher)
7. Si el script falla → informar al usuario

## Files to create/modify

| File | Action |
|------|--------|
| `scripts/linkedin-scraper.mjs` | 🆕 Crear — script Node.js Playwright |
| `.linkedin-cookies/auth-cookies.json` | 🆕 Crear — cookies de sesión (gitignorado) |
| `.linkedin-cookies/.gitkeep` | 🆕 Crear — mantener directorio en git |
| `specs/features/linkedin-playwright-scraper.md` | 🆕 Este spec |
| `.gitignore` | ✏️ Añadir `.linkedin-cookies/` |

## Dependencies

Node.js v18+ (tienes v21.4.0 ✅)
Playwright v1.61.1 (disponible vía npx)
macOS (tienes ✅)

No se requiere instalar nada globalmente — `npx playwright` gestiona los browsers automáticamente.

## Fallback plan

Si Playwright falla o las cookies expiran, el skill **no se queda bloqueado**. Cae a búsqueda web (Composio) como antes:

```
if (script_exitoso) → usar datos Playwright
else → buscar con websearch (fallback, modo degradado)
```

## Risks and mitigations

| Risk | Probability | Mitigation |
|------|------------|------------|
| LinkedIn detects headless | Baja | Fingerprint + headed mode opcional |
| Session cookies expire | Media | Aviso claro + --login mode |
| LinkedIn changes DOM | Media | CSS selectors con fallbacks |
| Rate limit bloquea IP | Baja | 2 búsquedas/día, delays humanos |
| Script bug rompe pipeline | Baja | Fallback a websearch siempre disponible |
