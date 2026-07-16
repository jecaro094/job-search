# Feature: Scoring dual — Technical Fit + Career Fit + Priority

## Trigger
- Evaluación de cualquier oferta que pase pre-filtros (job-matcher)
- Cálculo automático tras extracción de datos

## Problema
El scoring actual es monolítico (0-10) con pesos fijos que asumen que todas las empresas valoran lo mismo. Ignora factores como salario, cultura, dominio, o probabilidad de entrevista. Las decisiones de aplicación se basan solo en "match técnico" cuando deberían basarse en "prioridad estratégica".

## Solución: 3 scores independientes + Priority final

```
Technical Fit (0-100) → mide capacidad técnica
Career Fit    (0-100) → mide interés estratégico
Priority Score(0-100) → síntesis ponderada para ordenar
```

---

## 1. Technical Fit (50% del Priority)

### Pesos

| Factor | Peso | Notas |
|--------|------|-------|
| Python | 30% | Imprescindible. Si no aparece → Technical Fit capped a 40 máx |
| APIs / FastAPI / Django | 20% | Experiencia en diseño de APIs REST |
| Bases de datos SQL | 15% | PostgreSQL ideal. ORM counts. |
| Kafka / mensajería | 10% | Fuerte diferenciador, no blocker |
| Docker / AWS | 10% | Preferible, no obligatorio |
| Seniority match | 15% | Senior/Staff. Resta si pide Junior o Principal |

### Scoring no binario en lugar de cortes

**Publicación** (antes corte binario ≤7d):
| Antigüedad | Puntuación |
|------------|-----------|
| 0-7 días | +0 (neutral) |
| 8-14 días | -5 |
| 15-30 días | -10 |
| >30 días | -20 |
| Sin fecha | -15 |

**Tipo empresa** (antes corte binario product/no product):
| Tipo | Puntuación |
|------|-----------|
| Product company / startup | +15 |
| Engineering-first consultancy (plataforma interna, I+D, IA) | -5 |
| Consultora clásica / bodyshop | -20 |

**Empresa en múltiples plataformas**:
| Fuentes | Puntuación |
|---------|-----------|
| Aparece en 1 plataforma | +0 |
| Aparece en 2 plataformas | +5 |
| Aparece en 3+ plataformas | +10 |

---

## 2. Career Fit (50% del Priority)

| Factor | Peso | Descripción |
|--------|------|-------------|
| Salario estimado | 20% | ¿Está en rango 70-95k? ¿Equity? |
| Calidad del producto | 15% | ¿Producto que te gusta o te da igual? |
| Tamaño empresa | 10% | Startup/Scale-up ideal. Demasiado grande o pequeño resta |
| Dominio/industria | 10% | Fintech, healthcare, data, AI → mejor. Otros neutral |
| Cultura engineering | 15% | ¿Engineering blog? ¿Open source? ¿CTO técnico? |
| Crecimiento/estabilidad | 10% | Funding reciente, hiring activo, stage |
| Zona horaria | 10% | 100% compatible CET → ok. Diferencia ≤4h → ok. Mayor → resta |
| Stack moderno | 10% | ¿Python 3.12+? ¿FastAPI? ¿Cloud? ¿Modern tooling? |

---

## 3. Green Flags (bonus directo al Priority)

Cada green flag suma puntos directos. Se detectan en la descripción.

| Green Flag | Puntos | Cómo detectarlo |
|------------|--------|-----------------|
| ✅ Equipo pequeño (< 20 eng) | +3 | "small team", "lean engineering", "flat" |
| ✅ Ingeniería como core | +5 | "engineering-driven", "core product", "tech-first" |
| ✅ CTO técnico | +4 | "founded by engineers", "CTO ex-FAANG", "technical founders" |
| ✅ Funding reciente | +5 | "series [A/B/C]", "$X raised", "backed by" |
| ✅ Hiring activo | +3 | "growing team", "scaling rapidly", "multiple roles" |
| ✅ Open source | +4 | "open source", "OS contribution", "github" |
| ✅ Engineering blog | +3 | "engineering blog", "tech blog", "building in public" |
| ✅ CI/CD serio | +2 | "CI/CD", "deploy multiple times", "automated testing" |
| ✅ Ownership / autonomía | +3 | "ownership", "autonomy", "you will own", "from scratch" |
| ✅ Producto con propósito | +4 | Misión clara, impacto social/ambiental/tech |
| ✅ Cultura asíncrona | +3 | "async", "written communication", "docs over meetings" |
| ✅ Formación/presupuesto | +2 | "learning budget", "conference budget", "training" |

Máximo acumulable por green flags: **30 puntos**

---

## 4. Red Flags (penalización directa al Priority)

| Red Flag | Penalización | Cómo detectarlo |
|----------|-------------|-----------------|
| ❌ "rockstar" / "ninja" / "guru" | -10 | Términos exactos |
| ❌ "wear many hats" | -8 | Eufemismo de caos |
| ❌ "fast paced environment" | -6 | Horario intensivo |
| ❌ "must thrive under pressure" | -6 | Cultura de crunch |
| ❌ "family" (como valor de empresa) | -4 | Suele encubrir malas condiciones |
| ❌ "unlimited PTO" (sin mínimo) | -5 | Sin mínimo real = 0 días |
| ❌ Guardias frecuentes | -8 | "on-call rotation", "24/7 support" |
| ❌ >5 rondas de entrevista | -10 | "multi-stage", "5 rounds", "6 interviews" |
| ❌ Take home > 3h | -8 | "take home project", "homework assignment" |
| ❌ Salario oculto | -4 | No publica rango salarial |
| ❌ Consultora camuflada | -15 | "staff augmentation" disfrazado de "partner" |
| ❌ "must be in US" / solo US | -15 | Exclusión geográfica |
| ❌ Sin engineering manager | -6 | "no managers", "self-managed" (sin estructura) |

Penalización máxima acumulable: **-40 puntos**

---

## 5. Dificultad estimada

| Nivel | Criterios | Señales en la oferta |
|-------|-----------|---------------------|
| 🟢 Easy | Seniority mid, stack conocido, ≤3 rondas, sin Leetcode | "mid-level", stack tuyo, proceso simple |
| 🟡 Medium | Senior, algún gap técnico, 3-4 rondas | "senior", alguna tecnología nueva, take home optional |
| 🔴 Hard | Staff/Principal, stack nuevo, Leetcode, 5+ rondas | "staff", "system design", "leetcode", "coding challenge" |

---

## 6. Cálculo del Priority Score

```
Priority = (Technical_Fit × 0.50) + (Career_Fit × 0.50) + Green_Flags - Red_Flags - Difficulty_Penalty
```

Donde:
- **Difficulty_Penalty**: Easy = 0, Medium = -3, Hard = -7
- **Green_Flags**: capped at +30
- **Red_Flags**: capped at -40
- **Priority final**: clamped to [0, 100]

### Interpretación

| Priority | Acción |
|----------|--------|
| 85-100 | 🎯 Aplicar inmediatamente. Prioridad máxima. |
| 70-84 | 👍 Aplicar. Muy buena oportunidad. |
| 50-69 | 🤔 Considerar. Aplicar solo si el rol es muy interesante. |
| <50 | ❌ Descartar. No merece la pena. |

---

## 7. Output del job-matcher (nuevo formato)

```markdown
## Evaluación: [Empresa] — [Rol]

### Technical Fit: 82/100
| Factor | Peso | Score |
|--------|------|-------|
| Python | 30% | 100 |
| APIs/FastAPI | 20% | 80 |
| SQL | 15% | 70 |
| Kafka | 10% | 60 |
| Docker/AWS | 10% | 90 |
| Seniority | 15% | 80 |

### Career Fit: 74/100
| Factor | Peso | Score |
|--------|------|-------|
| Salario | 20% | 80 |
| Calidad producto | 15% | 85 |
| Tamaño empresa | 10% | 70 |
| Dominio | 10% | 90 |
| Cultura eng | 15% | 60 |
| Crecimiento | 10% | 80 |
| Zona horaria | 10% | 100 |
| Stack moderno | 10% | 60 |

### Green Flags (+15)
✅ Ingeniería como core (+5)
✅ Funding reciente (+5)
✅ CTO técnico (+4)
✅ Cultura asíncrona (+3)

### Red Flags (-6)
❌ "fast paced environment" (-6)

### Dificultad: 🟡 Medium (-3)

### Priority Score: (82×0.5) + (74×0.5) + 15 - 6 - 3 = **84/100** 👍

### Veredicto: Aplicar

### Por qué:
1. Stack casi idéntico (Python, FastAPI, AWS)
2. Empresa con funding reciente y cultura engineering
3. Salario en rango deseado
```

---

## 8. Almacenamiento (store-job actualizado)

Nuevas columnas en `data/jobs.csv`:

```
date, company, title, url, technical_fit, career_fit, priority_score, 
green_flags, red_flags, difficulty, verdict, summary, source_platforms
```

---

## 9. Estrategia de aplicación del flujo

Con el nuevo scoring, el flujo cambia:
- Ya no hay cortes binarios en fecha publicación, tipo empresa, etc.
- Los filtros estrictos **inamovibles** se mantienen: 100% remoto, backend/API/Data, full-time
- Todo lo demás se convierte en puntuación gradual
- Las ofertas se ordenan por **Priority Score** descendente
- Top 10 semanal se genera automáticamente
