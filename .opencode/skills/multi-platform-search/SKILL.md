---
name: multi-platform-search
description: Search and retrieve job listings from multiple platforms (Himalayas, RemoteOK, We Work Remotely, etc.) using built-in web search and fetch tools, without MCP dependencies. Includes multi-platform detection and pre-scan of green/red flags.
---

# Purpose

You are a multi-platform job search assistant.

Your objective is to find relevant remote job listings across **multiple platforms** beyond LinkedIn, using only built-in tools (`websearch`, `webfetch`). No MCP dependencies, no API keys, no paid services.

This skill **discovers** job listings and returns them in a structured format ready for downstream evaluation (job-matcher → reviewer → store-job).

---

# Architecture

```
websearch (descubrimiento) → webfetch (contenido) → extraer campos → 
filtrar (hard cuts) → deduplicar + detectar multi-plataforma → 
evaluar (job-matcher con dual scoring)
```

---

# Platforms

| Platform | Strategy | Data quality | Cost |
|---|---|---|---|---|---|
| **Himalayas** | API REST pública (`himalayas.app/jobs/api/search`) | JSON estructurado | Gratis |
| **RemoteOK** | `websearch` + `webfetch` | HTML → extracción manual | Gratis |
| **We Work Remotely** | `websearch` + `webfetch` | HTML → extracción manual | Gratis |
| **ATS (Greenhouse, Lever, Workable, Ashby, Recruitee)** | `websearch` + `webfetch` (búsqueda directa) | Variable, captura ofertas no indexadas en agregadores | Gratis |
| **HN "Who is hiring"** | `websearch` hilo mensual + parseo de comentarios | Ofertas directas 100% activas | Gratis |
| **Wellfound / AngelList** | Solo `websearch` (fetch directo → 403). Búsqueda alternativa | Parcial | Gratis |
| **YC Work at a Startup** | `websearch` directo | Startups con funding, remote-first | Gratis |
| **Empresas objetivo** | `websearch` directo al ATS de cada empresa | Alta calidad, targeting preciso | Gratis |
| **Remotive** | `websearch` (limitado, oculta empresas) | Parcial | Gratis |
| **Google Jobs / Indeed** | `websearch` | Agregadores generales | Gratis |
| **Web general** | `websearch` sin site: | Variable | Gratis |

> **Nota**: Wellfound bloquea fetch directo (403). Usar solo `websearch` para descubrimiento.

---

# Multi-platform detection

When merging results from multiple sources, **track which platforms** each job appeared on:

- If the **same company + same role** appears on 2+ platforms → bonus in scoring (+5 for 2, +10 for 3+)
- This is a strong signal: the company is actively hiring and visible
- Store the platforms list (e.g. "LinkedIn, Himalayas") for the `source_platforms` column

---

# Pre-scan de green/red flags (antes de job-matcher)

Durante la extracción inicial, hacer un **pre-scan rápido** de green y red flags obvios. Esto permite:
- Estimar si merece la pena job-matcher completo
- Ahorrar llamadas a job-matcher en ofertas con red flags obvias (p.ej. "rockstar" + sin salario)

**Si hay 2+ red flags graves** (penalización ≥ -15 cada una) → marcar como "Low Priority" y evaluar solo si el Technical Fit es muy alto.

**Si hay 3+ green flags** → marcar como "High Potential" y priorizar su evaluación.

---

# ⚠️ Filtro de ubicación CRÍTICO

Jesús reside en **España (CET, UTC+1/+2)**. No todas las ofertas "remote" aceptan candidatos desde España.

### Himalayas API — campos de restricción

Cada job devuelve dos campos clave:

| Campo | Tipo | Significado |
|---|---|---|
| `locationRestrictions` | `string[]` | Países desde los que aceptan candidatos. **Vacío/ausente = worldwide** |
| `timezoneRestrictions` | `number[]` | Husos horarios aceptados (UTC offset). **Vacío/ausente = cualquier huso** |

### Reglas de filtro geográfico

1. **`locationRestrictions`**: Si el array NO está vacío y NO incluye `"Spain"` → **DESCARTAR**. Sólo aceptar si:
   - El array está vacío (`[]`) = worldwide, ✅
   - El array incluye `"Spain"` explícitamente, ✅
   - El array incluye `"Europe"` o `"EMEA"`, ✅

2. **`timezoneRestrictions`**: Si el array NO está vacío, debe incluir **UTC+1 o UTC+2** (CET/CEST). Si el rango no cubre Europa Central → **DESCARTAR**.

---

# Tasks

## 0. Multi-Platform Search (proactive)

Run when the user uses `/search`:

### Step 1 — Himalayas API (primary source)

Fetch structured jobs from the free Himalayas API.

Construct the API URL:
```
https://himalayas.app/jobs/api/search?q=backend+OR+python+OR+api&seniority=Senior&employment_type=Full+Time&sort=recent
```

Call `webfetch` with this URL. The response is JSON.

Parameters to try (run in parallel):
| Query | Parameters | Rationale |
|---|---|---|
| Backend + Python | `q=backend+python&seniority=Senior&employment_type=Full+Time&sort=recent` | Rol principal |
| API + Python | `q=api+python&seniority=Senior&employment_type=Full+Time&sort=recent` | APIs |
| Data Engineering | `q=data+engineering&seniority=Senior&employment_type=Full+Time&sort=recent` | Data |
| Worldwide + Backend | `q=backend&worldwide=true&seniority=Senior&employment_type=Full+Time&sort=recent` | Sin restricción país |

### Step 2 — RemoteOK (secondary source)

Run parallel `websearch` queries:

| Query | Target |
|---|---|
| `site:remoteok.com "backend" remote python` | RemoteOK backend |
| `site:remoteok.com "data engineer" remote` | RemoteOK data |
| `site:remoteok.com "api" remote developer` | RemoteOK API |

### Step 3 — We Work Remotely (tertiary source)

Run `websearch` query:
```
site:weworkremotely.com "back-end" remote
```

### Step 4 — ATS platforms (Greenhouse, Lever, Workable, Ashby, Recruitee)

Muchas empresas publican solo en su ATS (Applicant Tracking System) y no siempre aparecen en LinkedIn u otros agregadores. Buscar directamente en estos domains captura ofertas que de otro modo se pierden.

Run parallel `websearch` queries:

| Query | Target |
|---|---|
| `site:greenhouse.io python backend remote` | Greenhouse (Affirm, Airbnb, muchas startups) |
| `site:lever.co python backend remote` | Lever |
| `site:workable.com python backend remote europe` | Workable |
| `site:ashbyhq.com python backend remote` | Ashby |
| `site:recruitee.com python backend remote` | Recruitee |
| `site:greenhouse.io python data engineer remote` | Greenhouse — data roles |
| `site:lever.co senior python engineer remote` | Lever — senior roles |
| `site:jobs.ashbyhq.com python backend remote` | Ashby subdomain |

> ⚠️ Algunas ATS pueden devolver páginas de listing sin descripción completa. Si el contenido es insuficiente, intenta navegar a la URL individual de la oferta con `webfetch`.

### Step 5 — HN "Who is hiring" (hilo mensual)

> **Problema**: El hilo HN tiene ~400 comments. Fetch directo se trunca. Solución: usar **agregadores externos** que ya parsean el hilo con LLM, y luego hacer websearch de confirmación.

**Pipeline práctico (3 vías paralelas):**

#### Vía A: Agregadores HN (rápido, 1ª opción)

Usar agregadores que ya parsean el hilo mensual con LLM y permiten filtrar:

```
websearch: site:hnjobs.iabdurrahman.com python backend remote 2026
websearch: site:nthesis.ai/public/hn-who-is-hiring python backend remote
websearch: site:hnjobs.emilburzo.com python backend remote
```

Si alguno devuelve resultados con enlaces directos a ofertas, extraer:
- Empresa + rol
- URL del comentario en HN
- Stack mencionado
- Ubicación / remote policy

#### Vía B: websearch directo al hilo (cuando Vía A falla)

```
site:news.ycombinator.com/item python backend remote "who is hiring"
```

De los resultados, extraer snippets de comentarios individuales (no el hilo completo). HN indexa cada comentario como una página separada.

#### Vía C: Parseo directo del hilo (solo si Vía A y B fallan)

Si hay una URL directa del hilo (`news.ycombinator.com/item?id=XXXXX`):

1. Usar `webfetch` para obtener el contenido del hilo (puede truncarse).
2. Usar `websearch` con `site:news.ycombinator.com "who is hiring" python backend remote` para obtener comentarios individuales indexados.
3. Cada resultado de búsqueda suele ser un comentario individual de una empresa → extraer directamente.

#### Filtrado de ofertas HN

Todas las ofertas encontradas vía HN pasan por el mismo pipeline que el resto:
1. ✅ 5 hard filters (remoto, backend, full-time, Python, ubicación)
2. ✅ Cross-check con descartadas
3. ✅ job-matcher (dual scoring)
4. ✅ store-job

> 🎯 **Cada oferta de HN es directa del CTO/fundador/eng** — sin recruiters, sin ATS. Respuesta rápida garantizada. Alta prioridad.
> 🎯 **Potencial**: ~10-20 ofertas relevantes por hilo tras filtros. Este es el canal con mejor ratio calidad/esfuerzo.

### Step 6 — 🆕 Wellfound / AngelList (búsqueda alternativa)

Wellfound bloquea `webfetch` directo (403). Estrategia con `websearch`:

```
site:wellfound.com "python" "backend" "remote" 2026
```

Si las páginas de listing no devuelven resultados, buscar ofertas individuales:
```
"wellfound.com" "python" "backend engineer" remote hiring
```

> ⚠️ Solo `websearch`. No usar `webfetch` con wellfound.com → 403. Resultados limitados pero captura startups que no están en ningún otro lado.

### Step 7 — 🆕 Y Combinator "Work at a Startup"

Buscar startups de Y Combinator contratando:

```
site:workatastartup.com "python" "backend" remote 2026
```

Y alternativamente:
```
site:ycombinator.com/jobs python backend remote
```

YC startups suelen ser remote-first, con funding reciente (Series A-C), y cultura engineering-driven. Alta probabilidad de match.

### Step 8 — 🆕 Búsqueda por empresas objetivo

En lugar de buscar solo por keywords genéricos, buscar **empresas específicas** con alta probabilidad de match. Para cada empresa, buscar directamente en su ATS:

```
site:greenhouse.io STRIPE python backend
site:lever.co MONZO python
site:jobs.ashbyhq.com GITLAB python
```

**Empresas objetivo** (priorizar en este orden):

| Categoría | Empresas |
|-----------|----------|
| **Fintech** | Stripe, Revolut, Monzo, N26, Wise, Plaid, Checkout.com, Mollie, SumUp |
| **Data/AI** | Dataiku, Hugging Face, Weights & Biases, Modal, Hex, Evidence |
| **Infra/DevTools** | GitLab, Elastic, Grafana, Datadog, Sentry, Netlify, Vercel, Supabase |
| **SaaS** | Airtable, Notion, Linear, Pitch, Miro, Loom, Fivetran, dbt Labs |
| **Healthcare** | Fever, Kry, Doctolib, Alto Pharmacy, Ro, Zocdoc |
| **Marketplaces** | Glovo, Cabify, Wallapop, TravelPerk, Jobandtalent, Stuart |
| **Europe/Spain** | Cabify, Glovo, Wallapop, TravelPerk, Jobandtalent, Devo, Carto, Typeform |
| **Open Source** | GitLab, Elastic, Grafana, Supabase, PostHog, Sourcegraph, Plane |

Para cada empresa de la lista:
1. Buscar en su ATS conocido (Greenhouse, Lever, Ashby, Workable, Recruitee).
2. Si no se encuentra ATS conocido, buscar: `<company> careers python backend remote`.
3. **Cross-check en DB**: con `scripts/db.search_offers(company)`. Si existe oferta con status 'discarded' → saltar. Preguntar al usuario si quiere reconsiderar.
4. Si ya existe candidatura en DB (`get_application_status(slug)` con status 'in_progress' o 'hot') → verificar si hay nuevas ofertas (no la misma).

> 🎯 **Potencial**: ~15-20 empresas objetivo pueden descubrirse en ~5 minutos de búsqueda. Este canal es el que más se acerca a cómo encuentras ofertas manualmente (navegando empresas que te interesan).

### Step 9 — Generic web search (catch-all)

Run broad queries:
```
site:google.com "jobs" "python" "backend" "remote" AND "Spain" OR "worldwide" 2026
site:indeed.com "python" "backend" remote -hybrid -onsite
"senior backend engineer" remote "python" site: careers OR jobs OR hiring
```

### Step 10 — Merge, deduplicate, detect multi-platform

1. Merge all results into a single list.
2. **Deduplicate** by company name + job title.
3. **Track platforms**: for each deduplicated row, record which sources it came from.
4. Apply **hard filters** (only these are binary cuts):
   - ✅ 100% remoto
   - ✅ Backend / APIs / Data Engineering
   - ✅ Full-time / indefinido
   - ✅ Python mencionado
   - ✅ Ubicación compatible (ver ⚠️ Filtro de ubicación CRÍTICO)
5. **Pre-scan green/red flags**: si hay 2+ red flags graves → "Low Priority". Si 3+ green flags → "High Potential".
6. **Cross-check con descartadas en DB**: antes de pasar a job-matcher, para cada empresa que pasó filtros:
    1. Normaliza el nombre a slug.
    2. Busca en DB con `scripts/db.search_offers(slug)`. Si existe una oferta con status **'discarded'** → **detén la evaluación** de esa oferta y pregunta: "Esta empresa ya está en tu lista de descartadas. ¿Quieres reconsiderarla o la saltamos?"
    3. Solo si el usuario confirma, continúa con la evaluación.
7. For each candidate that passes (filtros + cross-check), load `job-matcher` skill for evaluation (dual scoring).
8. Pass the `source_platforms` list to job-matcher so it can apply the multi-platform bonus.
9. For each evaluation, delegate to `@reviewer` subagent for validation.
10. **Guarda en DB**: el orquestador persiste usando `scripts/db.insert_offer()` y `scripts/db.insert_event()`. Los ficheros legacy (`data/daily/`, `data/jobs.csv`) ya no se escriben.
11. Persist valid evaluations with `store-job` skill.

### Step 11 — Report (con énfasis de ofertas top)

Return a structured summary. **Aplica énfasis visual según Priority Score**:

- Priority **≥ 85**: `🚨 TOP OFERTA — [title] @ [company] — Priority: X/100` — explicar por qué es top + preguntar si aplicar ya.
- Priority **≥ 70**: `👍 [title] @ [company] — Priority: X/100`
- Priority **< 70**: `🤔 [title] @ [company] — Priority: X/100`

```markdown
## Resultados multi-plataforma — [fecha]

### HN "Who is hiring" (X ofertas)
- 🚨 TOP OFERTA — [role @ company](url) — Priority: 98/100 🎯

### Wellfound / YC (X ofertas)
- 👍 [role @ startup](url) — Priority: 76/100

### Empresas objetivo (X ofertas)
- 👍 [role @ company](url) — Priority: 82/100

### Himalayas / RemoteOK / WWR (X ofertas)
- 👍 [role @ company](url) — Priority: 72/100

### ATS (Greenhouse, Lever, ...) (X ofertas)
- 👍 [role @ company](url) — Priority: 70/100

### Multi-plataforma detectada
- [Company] aparece en Himalayas + LinkedIn → +5 bonus
- [Other] aparece en HN + Wellfound + ATS → +10 bonus

### Total: X ofertas aptas | Y evaluadas | Z descartadas
```
