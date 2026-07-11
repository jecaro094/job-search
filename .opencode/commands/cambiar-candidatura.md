---
description: Cambia el estado de una candidatura en el sistema companies/
---

Cambia el estado de una empresa en el sistema de seguimiento: `/cambiar-candidatura $ARGUMENTS`

### Parámetros

```
/cambiar-candidatura <empresa> <nuevo_estado>
```

Estados válidos:
- `hot` o `🟢` — 🟢 Hot (en proceso activo, con entrevistas)
- `progress` o `🟡` — 🟡 In progress (candidatura enviada, esperando respuesta)
- `limbo` o `⚪` — ⚪ En el limbo (sin movimiento, pendiente de decisión)
- `rejected` o `🔴` — 🔴 Descartado (cerrado, no seguimiento)

### Flujo

1. Normaliza el nombre de la empresa a slug (minúsculas, espacios → guiones).
2. **Busca en DB** con `scripts/db.search_offers(slug)` para obtener el `offer_id`.
3. **Actualiza estado en DB** con `scripts/db.upsert_application(offer_id, slug, nuevo_estado)`.
4. **Registra evento** con `scripts/db.insert_event(offer_id, event_type, detail)` donde event_type es `applied`, `rejected`, o `manual_note` según el nuevo estado.
5. **Actualiza el fichero `companies/<slug>/STATUS.md`** si existe, para mantener consistencia visual (opcional).
6. Confirma el cambio y muestra el nuevo estado.

### Ejemplo

```
/cambiar-candidatura veriff hot
→ 🟢 Veriff marcada como Hot
```
