# Criterios de evaluación técnica

## Technical Fit (50% del Priority Score)

| Factor | Peso | Notas |
|--------|------|-------|
| Python | 30% | Imprescindible. Si no aparece → Technical Fit capped a 40 máx |
| APIs / FastAPI / Django | 20% | Experiencia fuerte en diseño de APIs REST |
| Bases de datos (SQL) | 15% | PostgreSQL ideal. ORM counts |
| Kafka / mensajería | 10% | Fuerte diferenciador, no blocker |
| Docker / AWS | 10% | Preferible, no obligatorio |
| Seniority match | 15% | Senior / Staff. Penaliza si pide Junior o Principal |

### Scoring no binario (con corte máximo)

**Fecha de publicación**: scoring gradual hasta 14 días. A partir de ahí, **hard cutoff**.
| Antigüedad | Puntuación |
|------------|-----------|
| 0-7 días | +0 (neutral) |
| 8-14 días | -5 |
| >14 días | ❌ **Descartar** (hard cutoff) |
| Sin fecha | -15 (scoring gradual, continúa evaluación) |

**Tipo de empresa** (antes corte binario product/no product):
| Tipo | Puntuación |
|------|-----------|
| Product company / startup | +15 |
| Consultora engineering (plataforma interna, I+D, IA) | **-5** |
| Consultora clásica / bodyshop | **-20** |

> Regla: Ningún tipo de consultora suma puntos. Como máximo son neutras, pero por definición tienen menor estabilidad/ownership que producto propio, así que siempre penalizan aunque sea mínimamente.

**Aparición multi-plataforma**:
| Fuentes | Puntuación |
|---------|-----------|
| 1 plataforma | +0 |
| 2 plataformas | +5 |
| 3+ plataformas | +10 |

---

## Career Fit (50% del Priority Score)

| Factor | Peso | Descripción |
|--------|------|-------------|
| Salario estimado | 20% | ¿Está en rango 70-95k? ¿Equity? |
| Calidad del producto | 15% | Producto interesante para el candidato |
| Tamaño empresa | 10% | Startup/Scale-up ideal (< 500 pers) |
| Dominio/industria | 10% | Fintech, healthcare, data, AI → mejor |
| Cultura engineering | 15% | Engineering blog, open source, CTO técnico |
| Crecimiento/estabilidad | 10% | Funding reciente, hiring activo, stage |
| Zona horaria | 10% | 100% CET ok, ≤4h diferencia ok |
| Stack moderno | 10% | Python 3.12+, FastAPI, cloud, tooling moderno |

---

## Green Flags (bonus directo al Priority)

| Green Flag | Puntos | Señal |
|------------|--------|-------|
| ✅ Equipo pequeño (< 20 eng) | +3 | "small team", "lean engineering" |
| ✅ Ingeniería como core | +5 | "engineering-driven", "tech-first" |
| ✅ CTO técnico | +4 | "founded by engineers", "CTO ex-FAANG" |
| ✅ Funding reciente | +5 | "series X", "$Y raised", "backed by" |
| ✅ Hiring activo | +3 | "growing team", "scaling rapidly" |
| ✅ Open source | +4 | "open source", "github", "OS" |
| ✅ Engineering blog | +3 | "engineering blog", "tech blog" |
| ✅ CI/CD serio | +2 | "CI/CD", "deploy multiple times" |
| ✅ Ownership / autonomía | +3 | "ownership", "autonomy", "from scratch" |
| ✅ Producto con propósito | +4 | Misión clara, impacto social/ambiental |
| ✅ Cultura asíncrona | +3 | "async", "docs over meetings" |
| ✅ Formación/presupuesto | +2 | "learning budget", "training" |

Máximo acumulable: **30 puntos**

---

## Red Flags (penalización directa al Priority)

| Red Flag | Penalización | Señal |
|----------|-------------|-------|
| ❌ "rockstar" / "ninja" / "guru" | -10 | Términos exactos |
| ❌ "wear many hats" | -8 | Eufemismo de caos |
| ❌ "fast paced environment" | -6 | Horario intensivo |
| ❌ "must thrive under pressure" | -6 | Cultura de crunch |
| ❌ "unlimited PTO" sin mínimo | -5 | Falso beneficio |
| ❌ Guardias frecuentes | -8 | "on-call rotation", "24/7" |
| ❌ >5 rondas entrevista | -10 | "multi-stage 5+" |
| ❌ Take home > 3h | -8 | "take home project" largo |
| ❌ Salario oculto | -4 | Sin rango salarial |
| ❌ Consultora camuflada | -15 | Staff aug disfrazado |
| ❌ Solo US / exclusión geográfica | -15 | "must be in US" |
| ❌ Sin engineering manager | -6 | "no managers", "self-managed" |

Penalización máxima: **-40 puntos**

---

## Dificultad estimada

| Nivel | Señales |
|-------|---------|
| 🟢 Easy | Mid-level, stack conocido, ≤3 rondas, sin leetcode |
| 🟡 Medium | Senior, algún gap técnico, 3-4 rondas |
| 🔴 Hard | Staff/Principal, Leetcode, system design, 5+ rondas, FAANG |

Penalización por dificultad: Easy=0, Medium=-3, Hard=-7

---

## Cálculo del Priority Score

```
Priority = (Technical_Fit × 0.50) + (Career_Fit × 0.50) + Green_Flags - Red_Flags - Difficulty_Penalty
```

Clamped a [0, 100].

| Priority | Acción |
|----------|--------|
| 85-100 | 🎯 Aplicar inmediatamente |
| 70-84 | 👍 Aplicar |
| 50-69 | 🤔 Considerar |
| <50 | ❌ Descartar |
