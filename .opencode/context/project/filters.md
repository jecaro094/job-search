# Filtros duros de búsqueda (cortes binarios)

Aplicar SIEMPRE antes de evaluar cualquier oferta. Si falla UNO → descartar sin evaluación.
No confundir con los criterios de scoring gradual (ver `@.opencode/context/core/criteria.md`).

---

## 1. Tipo de trabajo
- **Remoto 100%**. No híbrido, no presencial, no "remoto desde España" ambiguo.

## 2. Rol
- **Backend / APIs / Data Engineering**.
- **No**: frontend, fullstack con sesgo frontend, mobile, DevOps puro, management.

## 3. Tipo de contratación
- **Full-time / contrato indefinido**.
- **No**: freelancing, contracting temporal, B2B, part-time.

## 4. Python
- **Python debe estar mencionado explícitamente** en la oferta.
- Si no aparece → descartar. Si es ambiguo → descartar.

## 5. Ubicación geográfica
- **Debe aceptar candidatos desde España**.
- `locationRestrictions` debe estar vacío (worldwide), incluir "Spain", o incluir "Europe"/"EMEA".
- `timezoneRestrictions` debe cubrir CET/CEST (UTC+1 / UTC+2) o estar vacío.
- **No**: Solo US, solo India, solo UK sin Spain, etc.
- Si la oferta no especifica restricción → asumir worldwide ✅.

---

> ⚠️ **Lo que YA NO es corte binario** (ahora es scoring gradual):
> - Fecha de publicación → puntuación en Technical Fit (0-7d +0, 8-14d -5, etc.)
> - Tipo de empresa (product vs consultancy) → puntuación en Technical Fit (+15 a -20)
> - Multi-plataforma → bonus en Technical Fit (+5 a +10)
