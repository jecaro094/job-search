# Feature: Preparación de entrevistas

## Trigger

- Usuario escribe `prepárame para [empresa]`
- Skill `prepare-interview` cargada
- El orquestador detecta que una candidatura tiene un stage pendiente y sugiere preparación

## Inputs (fuentes de conocimiento)

El sistema extrae información de **cuatro capas** para preparar una entrevista:

| Capa            | Fuente                                                      | Propósito                                                          |
| --------------- | ----------------------------------------------------------- | ------------------------------------------------------------------ |
| **Candidatura** | `companies/<slug>/STATUS.md` + `NOTES.md` + `feedback_*.md` | Stage actual, rol, stack, feedback de fases previas                |
| **Proyectos**   | `projects/<slug>/`                                          | Experiencia documentada: STAR stories, trade-offs, arquitectura    |
| **CV**          | `cv/cv.md`                                                  | Perfil general, tecnologías, seniority                             |
| **Training**    | `tech-interview-archive/<slug>/`                            | Entrevistas pasadas: patrones de error, gaps, preguntas frecuentes |
| **Stack**       | `@.opencode/context/core/stack.md`                          | Stack técnico detallado del candidato                              |

## Proceso

### Fase 1: Cargar contexto de la empresa

1. Leer `companies/<slug>/STATUS.md` para determinar:
   - Estado actual de la candidatura (Hot / In progress / Limbo / Descartado)
   - Stage actual y siguientes
   - Timeline de eventos
   - Notas adicionales del proceso

2. Leer ficheros auxiliares en `companies/<slug>/`:
   - `NOTES.md` → notas de fit, salary, observaciones
   - `feedback_*.md` → feedback de fases anteriores (crítico para saber qué áreas evaluarán)

3. Si no existe la empresa en `companies/`, responder: "No tengo información sobre esa compañía. No puedo prepararte." y detenerse.

### Fase 2: Cross-reference con proyectos documentados

1. Leer `projects/README.md` para descubrir todos los proyectos disponibles.
2. Para cada proyecto, evaluar relevancia contra:
   - Stack técnico que pide la empresa
   - Tipo de role y responsabilidades
   - Área de evaluación del stage actual
3. Extraer de los proyectos relevantes:
   - **STAR stories** de `challenges.md` (Situation → Task → Action → Result)
   - **Trade-off examples** de `decisions.md` (alternativas consideradas, por qué se eligió cada una)
   - **Patrones arquitectónicos** de `architecture.md` que mapeen al dominio de la empresa
   - **Stack concreto** de `stack.md` para alinear vocabulario técnico

### Fase 3: Análisis de training data (entrevistas pasadas)

1. Leer `tech-interview-archive/README.md` para descubrir entradas disponibles.
2. **Company-matching**: buscar empresas con stack o dominio similar a la actual.
3. **Question-matching**: si en `interview-log.md` de otra empresa aparecen preguntas similares a las que podría hacer la empresa actual, identificarlas.
4. **Gap detection**: extraer `gap-analysis.md` de todas las entradas para detectar patrones de error del candidato.
5. Generar alertas si se detectan coincidencias:
   - "Esta empresa usa Kafka — en tu entrevista con [otra empresa] tuviste dificultades con Kafka partitioning. Repasa este concepto."
   - "Piden system design de streaming — tus gap-analysis muestran que es un área a reforzar."

### Fase 4: Generar material de preparación

Según el stage actual, generar contenido específico:

| Stage              | Contenido generado                                                                |
| ------------------ | --------------------------------------------------------------------------------- |
| **applied**        | Research de empresa: producto, stack, funding, cultura, engineering blog          |
| **hr-screening**   | Preguntas típicas de recruiter, salary expectations, motivation letter, 60s intro |
| **tech-interview** | Preguntas técnicas del stack, system design, conceptos distribuidos               |
| **live-coding**    | Ejercicios de coding en Python, pair programming simulado                         |
| **take-home**      | Planning de implementación, revisión de requisitos, estrategia de testing         |
| **system-design**  | Arquitectura, escalabilidad, trade-offs con ejemplos de `projects/`               |
| **cultural-fit**   | Valores de la empresa, preguntas comportamentales, STAR stories                   |
| **offer**          | Negociación, preguntas a hacer, comparativa de paquetes                           |

El output debe personalizarse con:

- Ejemplos concretos de `projects/` (STAR stories, trade-offs)
- Alertas de `tech-interview-archive/` (gaps detectados, preguntas similares)
- Recomendaciones de estudio priorizadas según patrones de error

## Output

```markdown
## Preparación para [Empresa] — [Rol]

### Stage actual: [Stage N] — [quién]

### Proyectos relevantes

- **[project]** → [qué conexión tiene con la empresa]
  - STAR story recomendada: [challenge]
  - Trade-off para mencionar: [decisión]

### ⚠️ Alertas de training data

- [alerta 1 basada en entrevistas pasadas]
- [alerta 2 basada en gaps detectados]

### Lo que debes repasar

- [tema 1 priorizado según gaps]
- [tema 2]

### Posibles preguntas

- [pregunta 1 con contexto de training data si aplica]
- [pregunta 2]

### Recursos

- [enlaces, docs, ejercicios recomendados]
```

## Integración con el `@interview-coach`

### Modo Coaching (práctica general)

Cuando el usuario pide practicar live coding o conceptos técnicos sin una empresa concreta:

1. El orquestador deriva a `@interview-coach`.
2. El coach lee `tech-interview-archive/` para identificar gaps y patrones de error.
3. El coach genera ejercicios específicos para las áreas débiles detectadas.

### Modo Repesca (rehacer entrevistas falladas)

Cuando el usuario quiere repetir una entrevista que ya falló y está documentada en `tech-interview-archive/`:

1. El orquestador deriva a `@interview-coach` con indicación del slug de la entrevista.
2. El coach carga `interview-log.md` de esa entrada para recuperar el enunciado exacto del problema.
3. El coach carga `gap-analysis.md` para saber qué falló la vez anterior.
4. El coach simula la sesión de nuevo, pero esta vez:
   - Aplica las lecciones del gap-analysis para que el usuario no repita el mismo error
   - Si el gap era "sobreoptimización", el coach frena al usuario si empieza a complicar
5. Al final, compara la nueva solución con el análisis anterior.

### Filosofía de interacción (modo tech interviewer)

En ambos modos, el coach actúa como un **tech interviewer real**, no como un tutor que da respuestas:

1. **Plantea el problema** sin solución adjunta.
2. **El usuario resuelve**, explicando su thought process en voz alta (como en una entrevista real).
3. **Hints progresivos**: si el usuario se atasca, el coach da pistas cada vez más específicas, nunca la solución completa.
4. **Discusión de trade-offs**: después de cada intento, se analizan alternativas, edge cases, complejidad.
5. **Solución de referencia**: solo se muestra al final, como parte del análisis comparativo ("tu enfoque vs solución de referencia").
6. **No juzgar, sino analizar**: el lenguaje es constructivo, nunca de "fallaste".

### Criterios de éxito del coach

- El usuario debe sentir que ha hecho un ejercicio de entrevista real, no que le han dado una clase.
- El coach debe detectar cuándo dar un hint y cuándo dejar que el usuario se equivoque (equivocarse también enseña).
- La solución de referencia solo se muestra **después** de que el usuario haya intentado resolverlo, no antes.
- El modo repesca debe evidenciar mejora respecto a la primera vez que se hizo el ejercicio.

## Criterios de éxito

- La preparación debe incluir **siempre** ejemplos de proyectos reales del candidato.
- Si hay training data disponible, debe incluir **siempre** alertas de gaps detectados.
- El material debe estar **adaptado al stage exacto** del proceso.
- Las STAR stories deben tener **métricas concretas** (Result con datos).
