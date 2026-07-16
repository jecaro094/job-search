---
description: Registra una candidatura enviada y crea seguimiento en companies/ + data/jobs.csv
---

He enviado mi candidatura a: $ARGUMENTS

1. Pide siempre, al menos, la url de la pagina de la oferta.
2. **Comprobar si ya existe una candidatura** chequeando `companies/<slug>/STATUS.md`. Si existe, decir `Ya tienes una candidatura para esta empresa. ¿Quieres crear otra o actualizar la existente?`
3. Guarda en Engram la decisión de aplicar (empresa, rol, fecha).
4. **Crea `companies/<slug>/STATUS.md`** con:
   - Estado: 🟡 In progress
   - Timeline: fecha actual + evento "Candidatura enviada"
   - Fuente: plataforma desde la que se aplicó
5. **Marca en `data/jobs.csv`**: añade columna "Applied" con la fecha si la oferta está en el CSV.
6. Pregúntame siempre si quiero añadir notas adicionales (persona de contacto, salario esperado, etc.). Dame estas opciones por terminal, de multiseleccion:
    - Añadir pregunta / respuesta de formulario.
    - Añadir información adicional.
7. Guarda la información adicional en `companies/<slug>/NOTES.md`.
8. Confirma el resumen de lo guardado.
