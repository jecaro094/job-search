# practice/ — Simulaciones de entrevistas técnicas

Ejercicios de práctica para entrevistas técnicas, organizados por empresa y tipo. El `@interview-coach` consulta esta carpeta para:

- No repetir ejercicios que ya se han trabajado
- Continuar la progresión (v1→v2→v3) en lugar de empezar de cero
- Detectar patrones de error en las prácticas (no solo en entrevistas reales)
- Tailorizar ejercicios según el feedback previo

---

## Convención de nombres

```
{empresa}-{tipo}-{n}.md
```

| Componente | Descripción | Ejemplo |
|------------|-------------|---------|
| `{empresa}` | Nombre corto de la empresa | `affirm`, `veriff`, `stripe` |
| `{tipo}` | Modalidad del ejercicio | `livecoding`, `sysdesign`, `sql`, `conceptos`, `star` |
| `{n}` | Número de secuencia | `1`, `2`, `3`... |

**Ejemplos reales:**
- `affirm-livecoding-1.md` — Primer live coding para Affirm
- `affirm-sysdesign-1.md` — Primer system design para Affirm
- `stripe-livecoding-1.md` — Primer live coding para Stripe

---

## Estructura interna de cada archivo

Cada ejercicio sigue esta plantilla:

```markdown
# {empresa}-{tipo}-{n} — {título descriptivo}

> **Fecha**: YYYY-MM-DD
> **Contexto**: Empresa, stage, formato
> **Interviewer simulado**: [nombre]

---

## Problema

[Enunciado completo]

### Input

[formato de entrada]

### Output

[formato de salida]

### Reglas de negocio

- [regla 1]
- [regla 2]

---

## Evolución del código (iteraciones)

### v1 — {cambio principal}
- [qué se hizo]
- **Problemas**: [qué fallaba]

### v2 — {cambio principal}
- [qué se hizo]
- **Problemas**: [qué fallaba]

### v{n} — {cambio principal}
- [qué se hizo]
- **Problemas**: [qué fallaba]

---

## Feedback general

### Fortalezas del candidato

1. [fortaleza 1]
2. [fortaleza 2]

### Áreas de mejora

1. [área 1]
2. [área 2]

### Consejo clave para {empresa}

[recomendación específica]

---

## Tags

`{empresa}` `{tipo}` `python` `fintech` (u otros según el dominio)

## Próximos pasos sugeridos

- [ ] [tarea pendiente 1]
- [ ] [tarea pendiente 2]
```

---

## Cómo se usa

### El `@interview-coach` lo consulta automáticamente

Cuando pidas un ejercicio, el coach mira primero `practice/` para ver si hay algo que continuar. No necesitas decirle.

### Tú puedes consultarlo manualmente

Los archivos están en markdown plano — se leen desde cualquier herramienta.

### Ejemplos de prompts para empezar una sesión

| Si dices... | El coach hará... |
|-------------|------------------|
| `"Prepárame para Affirm"` | Busca `practice/affirm-*`, ve la progresión existente, continúa desde el último feedback |
| `"Sigue con affirm-livecoding-1"` | Lee el archivo, retoma desde los próximos pasos pendientes |
| `"Practiquemos live coding"` | Busca el último ejercicio de live coding, si hay feedback pendiente lo retoma, si no propone uno nuevo |
| `"Me fue mal en la entrevista de Veriff"` | Modo Repesca: cruza con `tech-interview-archive/` + `practice/` para detectar patrones |
| `"Nuevo ejercicio para Stripe"` | Crea una entrada nueva en `practice/stripe-livecoding-1.md` (o el tipo que toque) |

---

## Diferencia con otras carpetas

| Carpeta | Contiene | Quién escribe |
|---------|----------|---------------|
| `practice/` | Simulaciones, ejercicios de práctica, feedback de iteraciones | El sistema (o manual) |
| `tech-interview-archive/` | Entrevistas reales que ya ocurrieron | El sistema (o manual) |
| `projects/` | Experiencia laboral documentada (STAR) | El sistema (o manual) |
| `companies/` | Estado de candidaturas activas | El sistema |
