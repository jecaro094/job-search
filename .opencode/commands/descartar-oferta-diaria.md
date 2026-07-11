---
description: Marca una oferta como descartada manualmente con razón y fecha. Persiste en data/jobs.db. No afecta a candidaturas.
---

Marca una oferta evaluada como descartada manualmente: `/descartar-oferta-diaria $ARGUMENTS`

### Parámetros

```
/descartar-oferta-diaria <empresa> [YYYY-MM-DD]
```

| Parámetro | Descripción | Obligatorio |
|-----------|-------------|:-----------:|
| `empresa` | Nombre o parte del nombre de la empresa (case-insensitive) | ✅ |
| `YYYY-MM-DD` | Fecha del discovery de la oferta. Si no se pasa, busca en todas las ofertas activas. | ❌ |

### Flujo

1. **Busca la oferta en la DB** usando `scripts/db.py`:
   ```python
   from scripts.db import search_offers, discard_offer
   
   # Buscar ofertas por nombre de empresa
   results = search_offers("enveritas")
   
   # Si se pasó fecha, filtrar por discovery_date
   # Si no, buscar en todas las activas
   ```

2. **Si no encuentra coincidencias**:
   - Muestra al usuario las ofertas activas disponibles.
   - Pregunta: "No encontré 'X'. Las ofertas activas son: A, B, C... ¿Quieres intentar con otro nombre?"

3. **Si encuentra múltiples coincidencias** (e.g., "Canonical" aparece dos veces):
   - Muestra las coincidencias numeradas con empresa, rol, fecha y priority.
   - Pregunta: "Varias coincidencias. ¿Cuál quieres descartar?" (opción múltiple).

4. **Pregunta interactivamente** (texto libre, obligatorio):
   - "Razón del descarte:" (p. ej.: "No me interesa el dominio", "Salario demasiado bajo", etc.)

5. **Actualiza la DB**:
   ```python
   from scripts.db import discard_offer
   discard_offer(offer_id, reason)
   ```

6. **Confirma la operación**:
   ```
   ✅ <Empresa> descartada
   Razón: <razón>
   ```

7. **Guarda en Engram** (`mem_save`) la decisión de descarte como `decision` con `topic_key: "manual-discard"`.

### Consideraciones

- **No modifica** la evaluación original de la oferta (ni su scoring, ni su veredicto).
- **No afecta** al sistema de candidaturas. Una oferta descartada manualmente NO es una candidatura.
- Si el usuario quiere **revertir** el descarte:
  ```python
  from scripts.db import get_conn
  conn = get_conn()
  conn.execute("UPDATE offers SET status = 'active' WHERE id = ?", (offer_id,))
  ```
- Al ejecutar `/descartar-oferta-diaria` sobre una oferta ya descartada, muestra:
  "⚠️ Esta oferta ya está descartada. ¿Quieres actualizar la razón?"

### Engram

Guardar como `type: decision`, `scope: project`, con `topic_key: "manual-discard"`.
