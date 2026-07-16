---
description: Marca una oferta como descartada manualmente con razón y fecha. Persiste en data/jobs.csv + log diario. No afecta a candidaturas.
---

Marca una oferta evaluada como descartada manualmente: `/descartar-oferta-diaria $ARGUMENTS`

### Parámetros
```
/descartar-oferta-diaria <empresa> [YYYY-MM-DD]
```

| Parámetro | Descripción | Obligatorio |
|-----------|-------------|:-----------:|
| `empresa` | Nombre o parte del nombre de la empresa (case-insensitive) | ✅ |
| `YYYY-MM-DD` | Fecha del discovery de la oferta. Si no se pasa, busca en el log de hoy. | ❌ |

### Flujo

1. **Busca la oferta en `data/jobs.csv`** o en `data/daily/YYYY-MM-DD.md`:
   - Busca por coincidencia de nombre.
   - Si se pasó fecha, buscar solo en ese log diario.

2. **Si no encuentra coincidencias**:
   - Muestra al usuario las ofertas activas disponibles en el CSV/log.
   - Pregunta: "No encontré 'X'. Las ofertas activas son: A, B, C... ¿Quieres intentar con otro nombre?"

3. **Si encuentra múltiples coincidencias** (e.g., "Canonical" aparece dos veces):
   - Muestra las coincidencias numeradas con empresa, rol, fecha y priority.
   - Pregunta: "Varias coincidencias. ¿Cuál quieres descartar?" (opción múltiple).

4. **Pregunta interactivamente** (texto libre, obligatorio):
   - "Razón del descarte:" (p. ej.: "No me interesa el dominio", "Salario demasiado bajo", etc.)

5. **Actualiza el log diario**:
   - Añade entrada en sección `### Descartadas manualmente` de `data/daily/YYYY-MM-DD.md`.

6. **Actualiza `data/jobs.csv`**: marca la fila como descartada (columna status = 'discarded').

7. **Confirma la operación**:
   ```
   ✅ <Empresa> descartada
   Razón: <razón>
   ```

8. **Guarda en Engram** (`mem_save`) la decisión de descarte como `decision` con `topic_key: "manual-discard"`.

### Consideraciones
- **No modifica** la evaluación original de la oferta (ni su scoring, ni su veredicto).
- **No afecta** al sistema de candidaturas. Una oferta descartada manualmente NO es una candidatura.
- Si el usuario quiere **revertir** el descarte: editar `data/jobs.csv` + eliminar entrada del log diario.
- Al ejecutar `/descartar-oferta-diaria` sobre una oferta ya descartada, muestra:
  "⚠️ Esta oferta ya está descartada. ¿Quieres actualizar la razón?"

### Engram
Guardar como `type: decision`, `scope: project`, con `topic_key: "manual-discard"`.
