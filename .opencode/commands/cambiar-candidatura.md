---
description: Cambia el estado de una candidatura editando companies/<slug>/STATUS.md
---

Cambia el estado de una candidatura: `/cambiar-candidatura $ARGUMENTS [estado]`

### Parámetros
- `$ARGUMENTS`: nombre de la empresa (texto libre, puede incluir comillas)
- `$2 [estado]`: nuevo estado (hot, in_progress, limbo, descartado)

### Flujo
1. Normaliza el nombre a slug.
2. **Busca `companies/<slug>/STATUS.md`** — si no existe, responde "No encontré candidatura para '$ARGUMENTS'."
3. **Actualiza `STATUS.md`**:
   - Cambia la línea `- **Status**:` al nuevo estado con emoji.
   - Añade entrada al Timeline con fecha y evento según el estado:
     - 🟢 Hot → "Candidatura priorizada"
     - 🟡 In progress → "Movimiento interno"
     - ⚪ Limbo → "Movida a limbo (sin novedades)"
     - 🔴 Descartado → Preguntar razón antes de cambiar
4. **Actualiza `data/jobs.csv`**: localiza la fila de la empresa y actualiza el estado si existe columna.
5. Confirma: "✅ `<Empresa>` actualizada a `<nuevo estado>`"
6. Guarda en Engram la decisión (`mem_save`, type: decision).
