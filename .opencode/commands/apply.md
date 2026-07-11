---
description: Registra una candidatura enviada y crea seguimiento en DB + companies/
---

He enviado mi candidatura a: $ARGUMENTS

1. Pide siempre, al menos, la url de la pagina de la oferta.
2. **Comprobar si ya existe una candidatura en DB** usando `scripts/db.search_offers(empresa)` y `scripts/db.get_application_status(slug)`. Si existe, decir `Existe una candidatura para esta empresa, que quieres hacer?`
    - Crear otra candidatura.
    - Comprobar si es la misma que ya existe.
3. Guarda en Engram la decisión de aplicar (empresa, rol, fecha).
4. **Persiste en DB** usando `scripts/db.upsert_application(offer_id, slug, 'in_progress')` y `scripts/db.insert_event(offer_id, 'applied', ...)`.
5. **Crea entrada en `companies/<slug>/`** con fichero `NOTES.md` para información adicional. (NOTA: STATUS.md ya no se escribe; la DB es la fuente de verdad para estados.)
6. Pregúntame siempre si quiero añadir notas adicionales (persona de contacto, salario esperado, etc.). Dame estas opciones por terminal, de multiseleccion:
    - Añadir pregunta / respuesta de formulario.
    - Añadir información adicional.
7. Guarda la información adicional en `companies/<slug>/NOTES.md`.
8. Confirma el resumen de lo guardado.
