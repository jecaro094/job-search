# Feature: Daily Evaluation Log

## Propósito

Persistir el **output completo y exhaustivo** de cada búsqueda y cada evaluación de `job-matcher` en un fichero markdown diario en `data/daily/YYYY-MM-DD.md`. 

Nunca se pierde información: cada búsqueda se documenta con **todas** las ofertas encontradas, **todas** las evaluaciones con desglose completo, y **todas** las métricas agregadas.

## ⚠️ Regla 1: APPEND, nunca overwrite

Cada búsqueda **añade** una sección nueva. Nunca se sobrescribe el contenido existente.

```
## Búsqueda HH:MM — [LinkedIn / Multi-platform / Individual match]

(contenido exhaustivo...)

*Búsqueda ejecutada: YYYY-MM-DD HH:MM*
```

Si el archivo no existe (primer evento del día), se crea con el encabezado general.

## ⚠️ Regla 2: Siempre se genera log, incluso si 0 evaluaciones

Aunque todas las ofertas sean descartadas en pre-filtros, **SIEMPRE** se genera una entrada en el daily log con:
- Queries ejecutadas
- Número de ofertas encontradas por canal
- Tabla completa de ofertas descartadas con URLs y motivo
- Métricas de búsqueda

La única excepción: si el orquestador no ejecutó ninguna búsqueda (ej: `/daily` sin búsqueda porque no habían pasado 12h).

## ⚠️ Regla 3: Toda evaluación lleva job-matcher COMPLETO

Cada oferta que pasa filtros recibe el desglose completo de job-matcher. No hay evaluaciones "de paso" sin desglose.

## Responsabilidad

El log diario es **responsabilidad del orquestador** (`@primary`). El orquestador escribe el log **después** de evaluar y validar con `@reviewer`, y **antes** de llamar a `store-job`.

## Trigger

- Tras cada `/search` → añade sección nueva
- Tras cada `/daily` → añade sección nueva
- Tras cada `/match <url>` → añade sección nueva

**Siempre se genera log**, haya o no ofertas evaluadas.

---

## Formato exhaustivo del fichero

### Encabezado (solo si el archivo no existe)

```markdown
# Daily Evaluation Log — YYYY-MM-DD
```

### Cada búsqueda → sección completa

Cada búsqueda genera una sección como esta:

---

## Búsqueda HH:MM — [LinkedIn / Multi-platform / Individual match]

> Contexto: [descripción breve de qué se buscó y por qué]

### Por canal

#### [Nombre del canal] (X ofertas — Y pasaron filtros)

**Queries ejecutadas:**
1. `query 1`
2. `query 2`

| Empresa | Rol | URL | Disposición | Motivo |
|---------|-----|-----|-------------|--------|
| Nombre | Título | `url completa` | ✅ Evaluada / ❌ Descartada | Razón exacta del descarte |

**Resultado**: X aptas para evaluación.

#### [Siguiente canal] (X ofertas — Y pasaron filtros)
...

### Evaluaciones detalladas (job-matcher completo)

Solo para las ofertas que pasaron filtros y fueron evaluadas. Una sección POR oferta.

## N. EMPRESA — Título del Rol

**URL**: `url completa y verificable`
**Source**: [LinkedIn / Himalayas / Greenhouse / etc.]
**Source URL**: `url directa de la oferta`
**Estado en sistema**: 🟢 Hot / 🟡 In progress / 🔴 Descartado / 🆕 Nueva

### Pre-filter (5 cortes binarios)
- ✅ 100% remoto — [Sí / No — razón si falla]
- ✅ Backend/API/Data — [Sí / No]
- ✅ Full-time — [Sí / No]
- ✅ Python — [Sí / No]
- ✅ Ubicación — [Spain / Worldwide / EMEA / CET compatible / razón si falla]

### Technical Fit: XX/100

| Factor | Peso | Score | Contribución |
|--------|------|-------|-------------|
| Python | 30% | XX | XX.X |
| APIs / FastAPI / Django | 20% | XX | XX.X |
| SQL / Databases | 15% | XX | XX.X |
| Kafka / messaging | 10% | XX | XX.X |
| Docker / AWS | 10% | XX | XX.X |
| Seniority match | 15% | XX | XX.X |
| **Base** | | | **XX** |
| Date adj | | ±X | |
| Company adj | | ±X | |
| Platform bonus | | +X | |
| **Total** | | | **XX** |

### Career Fit: XX/100

| Factor | Peso | Score | Contribución |
|--------|------|-------|-------------|
| Salary | 20% | XX | XX.X |
| Product quality | 15% | XX | XX.X |
| Company size | 10% | XX | XX.X |
| Domain | 10% | XX | XX.X |
| Eng culture | 15% | XX | XX.X |
| Growth | 10% | XX | XX.X |
| Timezone | 10% | XX | XX.X |
| Modern stack | 10% | XX | XX.X |
| **Total** | | | **XX** |

### Green Flags: +XX
- ✅ [flag concreto]: +X

### Red Flags: -XX
- ❌ [flag concreto]: -X

### Difficulty: 🟢 Easy / 🟡 Medium / 🔴 Hard
[Razón breve de por qué esta dificultad]

### Priority Score: XX/100 🎯👍🤔❌

```
Priority = (Tech×0.5) + (Career×0.5) + GreenFlags - RedFlags - Difficulty
         = (XX×0.5) + (XX×0.5) + XX - XX - X
         = XX
```

### Strengths
- [top 3 razones por las que esta oferta es buena para el candidato]

### Skill Gaps
- [tecnologías que pide la oferta y el candidato no domina, o debilidades]

### Verdict: [Apply immediately / Apply / Consider / Skip]

---

### Ofertas descartadas (completo)

Todas las ofertas que no pasaron pre-filtros, agrupadas por canal:

#### LinkedIn (X descartadas)

| Empresa | Rol | URL | Motivo |
|---------|-----|-----|--------|
| Ejemplo | Senior Python Backend | https://linkedin.com/... | Location: US only |

#### Himalayas (X descartadas)
...

#### ATS (X descartadas)
...

#### [Otros canales]
...

### Métricas de búsqueda

#### Por canal

| Canal | Examinadas | Pasaron pre-filtros | Evaluadas | 🎯 Apply | 👍 Apply | 🤔 Consider | ❌ Skip |
|-------|-----------|-------------------|-----------|----------|----------|-------------|--------|
| LinkedIn | X | X | X | X | X | X | X |
| Himalayas | X | X | X | X | X | X | X |
| ATS | X | X | X | X | X | X | X |
| HN | X | X | X | X | X | X | X |
| Wellfound | X | X | X | X | X | X | X |
| YC | X | X | X | X | X | X | X |
| RemoteOK | X | X | X | X | X | X | X |
| WWR | X | X | X | X | X | X | X |
| Empresas objetivo | X | X | X | X | X | X | X |
| Catch-all | X | X | X | X | X | X | X |
| **Total** | **X** | **X** | **X** | **X** | **X** | **X** | **X** |

#### Agrupado

| Métrica | Valor |
|---------|-------|
| Ofertas examinadas (brutas) | X |
| Pasaron pre-filtros | X |
| Evaluadas con scoring | X |
| 🎯 Apply immediately | X |
| 👍 Apply | X |
| 🤔 Consider | X |
| ❌ Skip | X |
| Canales que dieron resultados | X de Y |

### Observaciones / Notas
- [cualquier anomalía, problema técnico, o noting relevante, ej: "HN no parseado", "LinkedIn sin sesión devuelve solo US"]

---

*Búsqueda ejecutada: YYYY-MM-DD HH:MM*

---

## Consideraciones importantes

### URLs
- **Todas** las ofertas (evaluadas y descartadas) deben llevar URL completa y verificable.
- Si la URL es demasiado larga, usar formato `[enlace](url)` en markdown.
- No usar `https://...` ni placeholders. Si no hay URL, indicar "No disponible".

### Consistencia entre capas
- `data/search/YYYY-MM-DD/HH-MM-{channel}.json` contiene los mismos datos en bruto.
- `data/daily/YYYY-MM-DD.md` contiene el resumen estructurado.
- `data/jobs.csv` contiene las evaluaciones finales (solo las que pasaron @reviewer).
- Los tres deben ser coherentes: misma fecha, misma empresa, mismo score.

### Evaluaciones ya existentes
Si una oferta evaluada corresponde a una empresa que ya está en `companies/`:
- Indicar el estado actual: 🟢 Hot / 🟡 In progress / 🔴 Descartado
- No re-evaluar si ya está en `data/jobs.csv` con misma fecha (store-job ya hace dedup)
- Pero SÍ documentar en el log diario que se encontró y su estado actual
