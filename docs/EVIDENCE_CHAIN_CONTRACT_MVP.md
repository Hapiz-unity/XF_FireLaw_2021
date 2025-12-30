# Evidence Chain Contract (MVP)

## Purpose

The evidence-chain design provides a **neutral, non-judgmental** record of machine-captured IoT data at the time of work order check-in. This system:

- Presents raw factual data without interpretation
- Attaches metadata (units, sources) for transparency
- Maintains clear separation between human inspection and machine evidence
- Does not perform compliance checks, status judgments, or derive conclusions

## Definitions

### `iot_snapshot`

Machine-captured sensor data at the time of check-in. Contains:

- **pressure**: Numeric value (Float)
- **pump_running**: Boolean state (true/false)
- **timestamp**: ISO 8601 datetime string

**Semantics:**
- Represents a point-in-time snapshot, not a continuous stream
- Values are raw sensor readings, not interpreted status
- No "normal/abnormal" or "good/bad" labels

### `iot_snapshot_meta`

Metadata dictionary attached to `iot_snapshot` metrics. Provides:

- **unit**: Measurement unit (e.g., "MPa", "L/s", "A") or `null` if unknown
- **unit_source**: Origin of the unit information (e.g., "integrator_doc", "unknown")

**Semantics:**
- Only includes metadata for metrics that **actually exist** in `iot_snapshot`
- Does not invent metadata for missing metrics
- `null` when `iot_snapshot` is `null` (semantic consistency: no snapshot = no metadata)

### `point_meta.json`

Configuration file mapping point IDs (QR codes) to metric metadata. Located at:

- `apps/api/config/point_meta.json`

**Structure:**
```json
{
  "LOC001": {
    "metrics": {
      "pressure": { "unit": "MPa", "unit_source": "integrator_doc" },
      "flow": { "unit": "L/s", "unit_source": "unknown" },
      "current": { "unit": "A", "unit_source": "unknown" }
    }
  }
}
```

**Semantics:**
- Point-specific configuration (different points may have different units)
- Supports multiple metrics per point (pressure, flow, current)
- Fallback: `{"unit": null, "unit_source": "unknown"}` if point/metric not found

## Explicit Rules

### 1. No Compliance or Status Interpretation

- **Do NOT** convert values to "正常/异常" (normal/abnormal)
- **Do NOT** add green/red color coding based on values
- **Do NOT** derive compliance conclusions
- **Do NOT** add judgment language (e.g., "running" vs "stopped" for booleans)

**Example (correct):**
```json
{
  "pump_running": true
}
```

**Example (incorrect):**
```json
{
  "pump_running": "running",  // ❌ Do not convert boolean to string
  "status": "normal"          // ❌ Do not add interpretation
}
```

### 2. Raw Values Only

- Display values exactly as stored in database
- Booleans remain booleans (`true`/`false`, not strings)
- Numbers remain numbers (no string conversion)
- Timestamps remain ISO 8601 strings

### 3. Units Come from Metadata, Not Assumptions

- **Do NOT** hardcode units (e.g., always "MPa" for pressure)
- **Do NOT** assume units based on metric name
- **Always** use `iot_snapshot_meta` to determine units
- If metadata is missing, show value without unit or use fallback

**Example (correct):**
```json
{
  "iot_snapshot": { "pressure": 0.65 },
  "iot_snapshot_meta": {
    "pressure": { "unit": "MPa", "unit_source": "integrator_doc" }
  }
}
```

**Example (incorrect):**
```json
{
  "pressure": "0.65 MPa"  // ❌ Do not hardcode unit in value
}
```

### 4. Null Semantics

**Rule:** `iot_snapshot = null` => `iot_snapshot_meta = null`

- When no IoT snapshot exists, metadata must also be `null` (not `{}`)
- This maintains semantic consistency: absence of data = absence of metadata
- Empty object `{}` would imply "snapshot exists but has no metadata", which is incorrect

**Example (correct):**
```json
{
  "iot_snapshot": null,
  "iot_snapshot_meta": null
}
```

**Example (incorrect):**
```json
{
  "iot_snapshot": null,
  "iot_snapshot_meta": {}  // ❌ Empty object implies metadata exists
}
```

### 5. Metadata Only for Existing Metrics

- **Do NOT** attach metadata for metrics not present in `iot_snapshot`
- **Do NOT** invent flow/current values if they don't exist
- Only include metadata for metrics that have actual values

**Example (correct):**
```json
{
  "iot_snapshot": { "pressure": 0.65, "pump_running": true },
  "iot_snapshot_meta": {
    "pressure": { "unit": "MPa", "unit_source": "integrator_doc" }
    // pump_running excluded (boolean, no unit)
  }
}
```

**Example (incorrect):**
```json
{
  "iot_snapshot": { "pressure": 0.65 },
  "iot_snapshot_meta": {
    "pressure": {...},
    "flow": {...}  // ❌ flow not in snapshot
  }
}
```

## Example Responses

### With IoT Snapshot

```json
{
  "id": 1,
  "location": {
    "id": 1,
    "name": "消防泵房A",
    "qr_code": "LOC001"
  },
  "checkin_time": "2024-12-30T10:30:00",
  "pumphouse": "ok",
  "endpoint": "ok",
  "hydrant": "ok",
  "linkage": "ok",
  "conclusion": "所有设备运行正常",
  "iot_snapshot": {
    "pressure": 0.65,
    "pump_running": true,
    "timestamp": "2024-12-30T10:30:15"
  },
  "iot_snapshot_meta": {
    "pressure": {
      "unit": "MPa",
      "unit_source": "integrator_doc"
    }
  }
}
```

### Without IoT Snapshot

```json
{
  "id": 2,
  "location": {
    "id": 1,
    "name": "消防泵房A",
    "qr_code": "LOC001"
  },
  "checkin_time": "2024-12-30T11:00:00",
  "pumphouse": "ok",
  "endpoint": "ok",
  "hydrant": "ok",
  "linkage": "ok",
  "conclusion": null,
  "iot_snapshot": null,
  "iot_snapshot_meta": null
}
```

## Implementation Notes

- Backend endpoint: `GET /api/workorders/{id}`
- Metadata loader: `apps/api/services/point_meta.py`
- Config file: `apps/api/config/point_meta.json`
- Caching: In-memory module-level cache (no database queries)

## Future Extensions

When adding new metrics (e.g., flow, current):

1. Add metric to `point_meta.json` for relevant points
2. Add metric field to `IoTSnapshot` model (database migration)
3. Update metadata attachment logic in work order detail endpoint
4. **Do NOT** add interpretation logic or compliance checks

