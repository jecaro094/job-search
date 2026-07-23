# tech-interview-archive

Base de conocimiento de **entrevistas técnicas pasadas** para análisis de gaps, detección de patrones y preparación针对性.

---

## Cómo añadir una entrevista

Usa el skill `add-interview`. **Solo tienes que describir tu entrevista pasada en lenguaje natural** — el skill se encarga del resto:

```
Yo: Hice una entrevista en Veriff para Senior Backend Engineer. Llegué
     a la tercera ronda, un system design de verificación de documentos.
     Me pidieron Python, Kafka, PostgreSQL, AWS. En el system design me
     fue mal porque no supe estructurar los trade-offs entre síncrono
     y asíncrono. Me dijeron que mi experiencia en Python era sólida
     pero necesitaba más profundidad en sistemas distribuidos.

Sistema: Crea automáticamente:
         tech-interview-archive/veriff/
         ├── overview.md
         ├── interview-log.md
         ├── my-responses.md
         ├── feedback.md
         └── gap-analysis.md
```

No necesitas saber qué archivos crear ni qué estructura seguir. El skill:

1. Extrae la información clave de tu descripción (empresa, rol, fecha, stage, resultado, stack)
2. Te pregunta si faltan datos importantes (qué preguntaron, cómo respondiste, feedback)
3. Crea los 5 archivos con formato consistente
4. Actualiza este README con la entrada en el índice
5. Persiste en memoria para que el `@interview-coach` pueda usarlo en gap analysis
6. Si ya existe una entrada para esa empresa, te avisa y permite actualizarla

Puedes aportar la información **en varios turnos** — el skill itera y completa los archivos sin borrar lo anterior.

## Propósito

No se trata de un diario de fracasos, sino de un **sistema de aprendizaje continuo**. Cada entrevista que no sale bien es una fuente de datos para:

1. **Detectar patrones**: ¿siempre fallas en system design? ¿en live coding de asyncio? ¿en SQL?
2. **Priorizar entrenamiento**: el `@interview-coach` usará estos datos para enfocar ejercicios en tus áreas débiles.
3. **Company-matching inverso**: si una nueva empresa pregunta lo mismo que otra donde fallaste, el sistema te avisará y preparará específicamente.
4. **Evitar repetir errores**: las gap-analysis de cada entrada alimentan directamente el plan de estudio.

## Estructura

```
tech-interview-archive/
  README.md
  _template/                  # Plantilla para nuevas entradas
    overview.md
    interview-log.md
    my-responses.md
    feedback.md
    gap-analysis.md
  <company-slug>/             # Una carpeta por empresa
    overview.md
    interview-log.md
    my-responses.md
    feedback.md
    gap-analysis.md
```

## Formato de cada entrada

### `overview.md`

Datos generales de la entrevista:

```markdown
# [Nombre Empresa]

- **Rol**: Senior Backend Engineer
- **Fecha**: 2026-07-XX
- **Dónde la encontré**: LinkedIn / Himalayas / Referido / ...
- **Stage al que llegué**: HR screening / Tech interview / Live coding / System design / Cultural fit / Offer
- **Resultado**: ❌ Descartado en stage X
- **Stack que pedían**: Python, FastAPI, Kafka, PostgreSQL, ...
- **Seniority del rol**: Senior / Staff
```

### `interview-log.md`

Registro detallado de lo que preguntaron en cada etapa. Sé específico:

```markdown
## Stage 1 — HR Screening (2026-07-XX)

- Preguntas sobre experiencia previa
- Expectativas salariales
- ...

## Stage 2 — Tech Interview (2026-07-XX)

- **System design**: "Diseña un sistema de verificación de documentos"
- **Coding**: "Implementa un rate limiter thread-safe"
- **SQL**: "Query para detectar duplicados en una tabla de 10M filas"
- **Conceptos**: "Explica idempotencia en APIs REST"
```

### `my-responses.md`

Cómo respondiste. Sé honesto — esto es para que el sistema detecte gaps:

```markdown
## Lo que hice bien

- [acierto 1]
- [acierto 2]

## Lo que hice regular/mal

- [error 1]: explico por qué mi solución no era óptima
- [error 2]: no supe responder a X
```

### `feedback.md`

Feedback que te dieron (textual si lo recuerdas) + tu propio análisis:

```markdown
## Feedback recibido

> "Tu experiencia en Python es sólida, pero necesitas más profundidad en..."

## Mi interpretación

[Análisis propio de por qué crees que no pasaste]
```

### `gap-analysis.md`

Análisis estructurado de la carencia y plan de mejora:

```markdown
## Gap detectado

[Descripción concisa]

## Prioridad

🟢 Baja / 🟡 Media / 🔴 Alta

## Relacionado con proyectos

- [project-slug]: [breve descripción de experiencia relevante]

## Plan de mejora

1. [acción concreta 1]
2. [acción concreta 2]

## Referencias

- [enlaces a recursos, docs, ejercicios]
```

## Índice de entrevistas

| Empresa                           | Rol                                             | Fecha    | Stage alcanzado                                              | Gap principal                                                                      |
| --------------------------------- | ----------------------------------------------- | -------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| [Veriff](./veriff-system-design/) | Senior Backend Engineer — Verification Platform | Jul 2026 | Práctica: System Design (Verification Pipeline Orchestrator) | Clarificación de requisitos, arquitectura de componentes, data model, exactly-once |
| [Example 2 (anonimizado)](./example-2/) | Senior Python Developer (Django) | 2026 | Técnica — Refactor de endpoint legacy | En code review: hablar de problemas sin llegar a proponer código solución |
| [Example 1 (anonimizado)](./example-1/) | Senior Python Developer | Jun 2026 | Stage 2 — Primera técnica (coding) | Sobreoptimización inicial: priorizar solución funcional antes que óptima |

> Para añadir una entrada, describe tu entrevista pasada en lenguaje natural — el skill `add-interview` se encarga de crear los archivos y actualizar este índice automáticamente.

## Cómo lo usa el sistema

| Componente                | Uso de `tech-interview-archive/`                                                 |
| ------------------------- | -------------------------------------------------------------------------------- |
| `add-interview` skill     | Crea entradas nuevas a partir de descripciones en lenguaje natural               |
| `@interview-coach`        | Identifica gaps recurrentes, adapta ejercicios, sugiere plan de estudio. **Modo repesca**: recarga problemas de entrevistas falladas y simula la sesión aplicando las lecciones del gap-analysis |
| `prepare-interview` skill | Company-matching: busca si empresas similares preguntaron lo mismo que la actual |
| `@career-advisor`         | Reporta tendencias: "has fallado en 3 de 4 system design — prioriza eso"         |
| Orchestrator (AGENTS.md)  | Decide qué skill/subagente activar según el gap detectado                        |

## Cómo usar el coach para preparación técnica

El `@interview-coach` tiene **dos modos** de funcionamiento. En ambos actúa como un tech interviewer real: plantea problemas, guía con hints, discute trade-offs y solo muestra la solución de referencia al final.

### Modo Coaching (práctica general)

Para practicar live coding, system design, SQL o patrones distribuidos sin una empresa concreta:

```
Tú: Quiero practicar live coding para Affirm.

Coach: Aquí va un problema tipo Real World:
       [plantea el problema]

Tú: [resuelves explicando tu thought process]

Coach: [da hints si te atascas, nunca la solución]

       ---

Coach: Discutamos trade-offs y edge cases...
       [Al final, solución de referencia y comparación]
```

#### Cómo empezar

Di algo como:

> "Prepárame para la entrevista de Affirm. Quiero practicar live coding en Python."

O más específico:

> "Quiero practicar system design, el tema de diseño de sistemas con Kafka y event-driven."

El coach revisará tus gaps documentados, elegirá problemas relevantes y empezará la sesión.

### Modo Repesca (rehacer entrevistas falladas)

Para repetir una entrevista que ya fallaste y está documentada en el archive:

```
Tú: Quiero repetir el ejercicio del parser de Music Sales.

Coach: Vale. Recuerdo que la vez anterior tu gap fue
       "sobreoptimización inicial". Esta vez vamos a
       enfocarlo distinto: solución funcional primero,
       optimizar después. 45 minutos. ¿Empezamos?

       [Plantea el mismo problema que en example-1]
       [Si empiezas a complicar, te frena con un hint]
       [Al final, compara tu nueva solución con el gap anterior]
```

#### Cómo empezar

Di algo como:

> "Quiero repetir la entrevista de example-1 en modo repesca."

O:

> "Rehagamos el problema del parser de Music Sales aplicando la lección."

El coach cargará el enunciado del `interview-log.md` y el gap del `gap-analysis.md` para adaptar la sesión.

### Filosofía del coach

- ✅ **Hints progresivos** — pistas cada vez más específicas, nunca la respuesta
- ✅ **Discusión de trade-offs** después de cada intento
- ✅ **Solución de referencia solo al final** — primero tú, luego la comparación
- ✅ **Lenguaje constructivo** — no se juzga, se analiza
- ✅ **Detección de patrones** — si tienes un gap recurrente, el coach lo sabe y adapta los ejercicios

La especificación completa está en `specs/features/interview-prep.md`.

---

_Creado en julio 2026 como parte del sistema job-search._
