# Feature: Preparación de entrevistas

## Trigger
- Usuario pregunta "prepárame para [empresa]"
- Skill `prepare-interview` cargada

## Proceso
1. Verificar que existe candidatura en DB con `scripts/db.get_application_status(slug)`.
2. Leer estado actual desde DB (events table) y desde `companies/<slug>/STATUS.md` si existe (legacy) para conocer el stage detallado.
3. Según el stage, preparar contenido específico:
   - **applied** → research sobre la empresa, productos, stack.
   - **hr-screening** → preguntas típicas de RRHH, motivation letter.
   - **tech-interview** → sistema de preguntas técnicas, algoritmos, system design.
   - **live-coding** → pair programming, ejercicios prácticos.
   - **take-home** → revisión de la prueba, planning de implementación.
   - **system-design** → arquitectura, escalabilidad, trade-offs.
   - **cultural-fit** → valores de la empresa, preguntas de comportamiento.
   - **offer** → negociación, qué preguntar.
4. Generar material de estudio personalizado basado en el stack del candidato.

## Output
```markdown
## Preparación para [Empresa] - Stage: [stage]

### Lo que debes repasar
- ...

### Posibles preguntas
- ...

### Recursos
- ...
```
