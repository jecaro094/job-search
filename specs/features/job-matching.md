# Feature: Evaluación individual de oferta

## Alcance

Este spec cubre el pipeline **B** de evaluación de una oferta individual, típicamente encontrada por el usuario en su navegación manual.

## Trigger

- Comando `/match <url>`
- Usuario comparte URL de oferta durante la conversación

## Dependencias

| Recurso | Rol |
|---------|-----|
| `@job-analyst` subagent | Extraer datos estructurados de la URL |
| `job-matcher` skill | Evaluación dual (Technical Fit + Career Fit → Priority) |
| `store-job` skill | Persistencia en `data/jobs.csv` |
| `@reviewer` subagent | Validación de la evaluación |
| `@.opencode/context/project/filters.md` | 5 filtros duros |
| `@.opencode/context/core/criteria.md` | Pesos, flags, dificultad |
| `@.opencode/context/core/stack.md` | Stack técnico del candidato |

---

## Pipeline B — Evaluación individual (`/match`)

### 1. Extraer datos con @job-analyst

El subagente `@job-analyst` extrae de la URL:

- **Empresa**: nombre, tamaño, tipo (product/consultora/startup)
- **Rol**: título, seniority, responsabilidades
- **Stack**: lenguajes, frameworks, infraestructura, bases de datos
- **Ubicación**: remoto, país, huso horario
- **Contrato**: full-time / freelance / contracting
- **Salario**: si está publicado
- **Fecha de publicación**: si está disponible
- **Proceso de entrevista**: número de rondas, take-home, leetcode
- **Descripción completa**: texto del anuncio

### 2. Cross-check con descartadas

- Normalizar nombre de empresa a slug.
- Si existe `companies/<slug>/STATUS.md` con status 🔴 Descartado → **detener y preguntar** al usuario.
- Solo continuar si el usuario confirma.

### 3. Pre-filters (5 cortes binarios)

| # | Filtro | Si falla |
|---|--------|----------|
| 1 | 100% remoto | ❌ Descartar |
| 2 | Backend / APIs / Data Engineering | ❌ Descartar |
| 3 | Full-time / indefinido | ❌ Descartar |
| 4 | Python mencionado explícitamente | ❌ Descartar |
| 5 | Ubicación: Spain o worldwide | ❌ Descartar |

> Si no hay fecha de publicación → continuar con penalización -15 en Technical Fit (no es hard cutoff).

### 4. Evaluación con job-matcher (dual scoring)

Cargar skill `job-matcher` con los datos extraídos. Calcula:

1. **Technical Fit (0–100)**: 6 factores ponderados + adjustments (fecha, tipo empresa, multi-plataforma).
2. **Career Fit (0–100)**: 8 factores ponderados (salario, producto, tamaño, dominio, cultura, crecimiento, timezone, stack moderno).
3. **Green Flags**: hasta +30 en señales positivas.
4. **Red Flags**: hasta -40 en señales de alerta.
5. **Difficulty**: 🟢 Easy (0) / 🟡 Medium (-3) / 🔴 Hard (-7).
6. **Priority Score**: `(Tech × 0.5) + (Career × 0.5) + Green - Red - Difficulty`. Clamped [0, 100].

### 5. Guardar log diario

El orquestador escribe las métricas completas en `data/daily/YYYY-MM-DD.md` con el formato definido en `specs/features/daily-log.md`.

### 6. Validar con @reviewer

El subagente `@reviewer` verifica:
- Consistencia de los scores.
- Correcta aplicación de pre-filtros.
- Coherencia entre flags, dificultad y veredicto.
- Que no se haya descartado incorrectamente por tipo de empresa.

### 7. Persistir con store-job

Guarda resumen en `data/jobs.csv`. Si la empresa ya existe, notifica sin duplicar.

---

## Post-procesamiento

- Priority **≥ 85** → `🚨 TOP OFERTA — [title] @ [company] — Priority: X/100`. Explicar por qué es top + preguntar si aplicar ya.
- Priority **≥ 70** → `👍 [title] @ [company] — Priority: X/100`
- Priority **< 70** → `🤔 [title] @ [company] — Priority: X/100`
- Priority **< 50** → `❌ [title] @ [company] — Skip`

## Recomendaciones por rol

| Priority | Acción |
|----------|--------|
| 85-100 | 🎯 Aplicar inmediatamente |
| 70-84 | 👍 Aplicar |
| 50-69 | 🤔 Considerar aplicación |
| <50 | ❌ Skip |
