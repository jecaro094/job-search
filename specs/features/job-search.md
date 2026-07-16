# Feature: Búsqueda proactiva diaria

## Alcance

Este spec cubre los pipelines de descubrimiento y evaluación de ofertas. Se ejecuta bajo demanda (`/search`).

## Triggers

- Comando `/search`
- Manual (el orquestador carga el spec y ejecuta los pasos relevantes)

## Dependencias

| Recurso | Rol |
|---------|-----|
| `multi-platform-search` skill | Obtener ofertas de Himalayas, HN, RemoteOK, WWR, ATS |
| `multi-platform-search` skill | Obtener ofertas de Himalayas, RemoteOK, WWR, ATS, HN, Wellfound |
| `job-matcher` skill | Evaluación dual (Technical Fit + Career Fit → Priority) |
| `store-job` skill | Persistencia en `data/jobs.csv` |
| `@reviewer` subagent | Validación de evaluaciones |
| `@.opencode/context/project/filters.md` | 5 filtros duros |
| `@.opencode/context/core/criteria.md` | Pesos, flags, dificultad |
| `@.opencode/context/core/stack.md` | Stack técnico del candidato |

---

## Búsqueda LinkedIn (optativa, preguntar siempre)

> **🆕 Ahora con Playwright.** Ya no se usa websearch de Composio. El scraper usa una sesión real de LinkedIn para acceder directamente a LinkedIn Jobs. Ver `specs/features/linkedin-playwright-scraper.md` para detalles.

> ⚠️ **Siempre preguntar antes.** Antes de ejecutar cualquier búsqueda LinkedIn, preguntar al usuario: "¿Quieres que busque en LinkedIn hoy?" Si dice que no, saltar LinkedIn. El resto de canales multi-plataforma no se ven afectados.

### 1. Preguntar al usuario
Antes de nada, preguntar explícitamente: *"¿Quieres que busque en LinkedIn hoy? (tarda 3-5 minutos)"*
- **No** → abortar. Saltar a búsqueda multi-plataforma si corresponde.
- **Sí** → continuar.

### 2. Cargar skill
```yaml
skill: multi-platform-search
```

### 3. Rate limit check
- Leer `data/.linkedin-rate-limit.json`.
- Si **≥ 2 ejecuciones hoy** → **bloquear** con mensaje explícito. No continuar.
- Si **< 2** → continuar.

### 4. Ejecutar scraper Playwright
```bash
node scripts/linkedin-scraper.mjs
```
Tiempo estimado: **3-5 minutos**. Las 3 queries se ejecutan secuencialmente con delays humanos.

### 4. Leer resultados
- Buscar el archivo más reciente en `data/search/YYYY-MM-DD/*-linkedin-playwright.json`.
- Extraer `results`.

### 5. Actualizar rate limit
- Añadir timestamp actual a `executions_today` en `data/.linkedin-rate-limit.json`.

### 6. Cross-check con descartadas
- Normalizar nombre de empresa a slug.
- Si existe `companies/<slug>/STATUS.md` con status 🔴 Descartado → **detener y preguntar** al usuario.
- Solo continuar si el usuario confirma.

### 7. Pre-filters (5 cortes binarios)
| # | Filtro | Si falla |
|---|--------|----------|
| 1 | 100% remoto | ❌ Descartar |
| 2 | Backend / APIs / Data Engineering | ❌ Descartar |
| 3 | Full-time / indefinido | ❌ Descartar |
| 4 | Python mencionado explícitamente | ❌ Descartar |
| 5 | Recencia ≤ 14 días | ❌ Descartar si >14d |

> Company type (product vs consultora) **no** es filtro binario — se puntúa gradualmente en job-matcher.

### 8a. Guardar resultados brutos
Ya los guarda el scraper en `data/search/YYYY-MM-DD/HH-MM-linkedin-playwright.json`.

### 8b. Evaluación con job-matcher
### 9. APPEND log diario en `data/daily/YYYY-MM-DD.md`
**IMPORTANTE**: Añadir una nueva sección `## Búsqueda HH:MM — [Tipo]`, **no sobrescribir** el archivo. Ver `specs/features/daily-log.md`.

### 10. Validar con @reviewer
### 11. Persistir con store-job

---

## Búsqueda multi-plataforma (`/search`)

> **Objetivo**: cubrir canales que LinkedIn no indexa bien: agregadores remotos (Himalayas, RemoteOK, WWR), ATS directos (Greenhouse, Lever, etc.), startups (Wellfound, YC), y ofertas del momento (HN Who is hiring).

### 1. Cargar skill
```yaml
skill: multi-platform-search
```

### 2. Himalayas API (4 queries paralelas)

| Query | Parámetros |
|-------|-----------|
| Backend + Python | `q=backend+python&seniority=Senior&employment_type=Full+Time&sort=recent` |
| API + Python | `q=api+python&seniority=Senior&employment_type=Full+Time&sort=recent` |
| Data Engineering | `q=data+engineering&seniority=Senior&employment_type=Full+Time&sort=recent` |
| Worldwide + Backend | `q=backend&worldwide=true&seniority=Senior&employment_type=Full+Time&sort=recent` |

### 3. RemoteOK (3 queries paralelas)

| Query |
|-------|
| `site:remoteok.com "backend" remote python` |
| `site:remoteok.com "data engineer" remote` |
| `site:remoteok.com "api" remote developer` |

> ⚠️ RemoteOK tiene ofertas caducadas. Verificar recencia estrictamente (>14d → descartar). No confiar en que la página esté activa.

### 4. We Work Remotely (1 query)
`site:weworkremotely.com "back-end" remote`

### 5. ATS platforms (8 queries paralelas)

| Query | Target |
|-------|--------|
| `site:greenhouse.io python backend remote` | Greenhouse |
| `site:lever.co python backend remote` | Lever |
| `site:workable.com python backend remote europe` | Workable |
| `site:ashbyhq.com python backend remote` | Ashby |
| `site:recruitee.com python backend remote` | Recruitee |
| `site:greenhouse.io python data engineer remote` | Greenhouse (data) |
| `site:lever.co senior python engineer remote` | Lever (senior) |
| `site:jobs.ashbyhq.com python backend remote` | Ashby subdomain |

### 6. 🆕 HN "Who is hiring" — hilo mensual
```
site:news.ycombinator.com "who is hiring" "remote" "python" 2026
```
También buscar el hilo agregado:
```
site:hackernewsjobs.com python backend remote
```

Si se encuentra el hilo, parsear los comentarios en busca de ofertas que mencionen:
- Python + backend / data / api
- Remote / remote-friendly
- Senior / staff

Cada comentario suele ser una oferta directa del CTO/fundador. Prioridad alta porque son 100% activas.

### 7. 🆕 Wellfound / AngelList (búsqueda alternativa)
Wellfound bloquea fetch directo (403). Estrategia:
```
websearch: site:wellfound.com "python" "backend" "remote" 2026
```
Si las páginas de listing no cargan, buscar ofertas individuales:
```
websearch: "wellfound.com" "python" "backend engineer" remote hiring
```

> No usar `webfetch` directo a wellfound.com → 403. Solo `websearch`.

### 8. 🆕 Y Combinator "Work at a Startup"
```
websearch: site:workatastartup.com "python" "backend" remote 2026 OR site:ycombinator.com/jobs python backend remote
```
YC startups suelen ser remote-first, con funding reciente y buen engineering culture.

### 9. 🆕 Búsqueda por empresas objetivo
En lugar de solo keywords, buscar empresas **específicas** con alta probabilidad de match. Para cada empresa conocida o descubierta, buscar directamente en su ATS:

```
site:greenhouse.io <company> python backend
site:lever.co <company> python backend
site:jobs.ashbyhq.com <company> python
```

Empresas a priorizar (alta probabilidad de match):
- **Fintech**: Stripe, Revolut, Monzo, N26, Wise, Plaid, Checkout.com, Mollie
- **Data/AI**: Dataiku, Databricks, Hugging Face, Weights & Biases, Modal
- **Infra/DevTools**: GitLab, Elastic, Grafana, Datadog, Sentry, Netlify, Vercel
- **SaaS**: Airtable, Notion, Linear, Pitch, Miro, Figma (backend roles)
- **Healthcare**: Fever, Kry, Doctolib, Alto Pharmacy, Ro
- **Marketplaces**: Glovo, Cabify, Wallapop, TravelPerk, Jobandtalent

> La idea es **buscar activamente** en los ATS de estas empresas, no esperar a que aparezcan en búsquedas genéricas. Este es el canal que más ofertas de alta calidad aporta y que usaste tú para encontrar Affirm (Greenhouse) y Veriff (Greenhouse).

### 10. 🆕 Catch-all: Google Jobs / Indeed
```
site:google.com "jobs" "python" "backend" "remote" AND "Spain" OR "worldwide" 2026
site:indeed.com "python" "backend" remote -hybrid -onsite
```

### 11. Merge + dedup + detectar multi-plataforma
- Unificar todos los resultados.
- Deduplicar por empresa + rol.
- Registrar fuentes (si una oferta aparece en 2+ fuentes → bonus +5/+10 en scoring).

### 12. Pre-scan green/red flags
- Si 2+ red flags graves (≥ -15 c/u) → marcar "Low Priority".
- Si 3+ green flags → marcar "High Potential".

### 13. Cross-check con descartadas
### 14. Pre-filters (5 cortes binarios)
### 14a. Guardar resultados brutos en `data/search/YYYY-MM-DD/HH-MM-{channel}.json`
Persistir resultados crudos de **cada canal** (himalayas, ats, hn, wellfound, etc.) en archivos JSON separados. Ver `specs/features/search-persistence.md`.

### 15. Evaluación con job-matcher
### 16. APPEND log diario en `data/daily/YYYY-MM-DD.md`
Añadir sección nueva, **no sobrescribir**.

### 17. Validar con @reviewer
### 18. Persistir con store-job



## Post-procesamiento (común a todos los pipelines)

### Notificación de ofertas top
- Priority **≥ 85** → `🚨 TOP OFERTA — [title] @ [company] — Priority: X/100`. Explicar por qué es top + preguntar si aplicar ya.
- Priority **≥ 70** → `👍 [title] @ [company] — Priority: X/100`
- Priority **< 70** → `🤔 [title] @ [company] — Priority: X/100`

### Formato del reporte diario

```
## Resultados de búsqueda — YYYY-MM-DD

### LinkedIn (X ofertas — Y pasaron filtros)
- 🚨 TOP OFERTA — ...

### Multi-plataforma (X ofertas — Y pasaron filtros)
- HN Who is hiring: X ofertas
- Wellfound/YC: X ofertas
- Himalayas/RemoteOK/WWR: X ofertas
- ATS: X ofertas
- Empresas objetivo: X ofertas

### Ofertas descartadas
| Empresa | Fuente | Motivo |

### Total: X ofertas aptas | Y evaluadas | Z descartadas
```

El orden de ejecución real del `/daily` está definido en `.opencode/commands/daily.md`.
