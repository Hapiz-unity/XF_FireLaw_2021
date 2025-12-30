# Demo Guide (MVP)

## Starting the System

### Backend (FastAPI)

```bash
cd apps/api
python main.py
```

Backend will start at http://localhost:8000

Alternatively, using uvicorn directly:

```bash
cd apps/api
uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd apps/web
npm install  # First time only
npm run dev
```

Frontend will start at http://localhost:3000

### One-Command Startup

If `start.sh` is available:

```bash
./start.sh
```

This starts both backend and frontend concurrently.

## Demo URLs

### Work Orders List

**URL:** http://localhost:3000/workorders

**What it demonstrates:**
- List view of all work orders
- Manual inspection summary badges (pumphouse, endpoint, hydrant, linkage)
- IoT snapshot indicators (pressure and pump_running values, or "View in detail" link)
- Location information (name and QR code)
- Check-in timestamps
- Each row links to the detail page

### Work Order Detail (With IoT Snapshot)

**URL:** http://localhost:3000/workorders/1

**What it demonstrates:**
- Complete evidence chain with IoT snapshot
- Location & Check-in section: location name, QR code, check-in time, inspector conclusion
- Manual Inspection Summary: human-reported status for each inspection point (ok/issue badges)
- IoT Evidence Record: machine-captured snapshot with metadata
  - Evidence type, point ID, captured timestamp (formatted and ISO)
  - Pressure value with unit from metadata (e.g., "0.65 MPa")
  - Pump running state (boolean: true/false)
  - All values presented neutrally without interpretation

**Expected data:**
- Work order ID 1 has IoT snapshot with pressure unit from `point_meta.json`
- `iot_snapshot_meta.pressure.unit` is populated (e.g., "MPa")

### Work Order Detail (Without IoT Snapshot)

**URL:** http://localhost:3000/workorders/5

**What it demonstrates:**
- Same structure as work order with IoT snapshot
- Location & Check-in section: complete
- Manual Inspection Summary: complete
- IoT Evidence Record: empty state
  - Shows neutral message: "No IoT evidence snapshot attached to this work order."
  - Demonstrates null handling: `iot_snapshot = null`, `iot_snapshot_meta = null`

**Expected data:**
- Work order ID 5 has no IoT snapshot
- API returns `iot_snapshot: null` and `iot_snapshot_meta: null`

## Demo Data Structure

The seed data includes:

- **3 locations:** LOC001, LOC002, LOC003
- **5 work orders:**
  - IDs 1-4: WITH IoT snapshots (evidence chain demo)
  - ID 5: WITHOUT IoT snapshot (null handling demo)

Work orders 1-2 use LOC001, work orders 3-4 use LOC002, and work order 5 uses LOC003. All locations have metadata configured in `apps/api/config/point_meta.json` for pressure units.

## What Each Page Demonstrates

### List Page (`/workorders`)

- **Purpose:** Overview of all maintenance work orders
- **Key features:**
  - Table/list layout with work order ID, location, check-in time
  - Manual inspection badges showing ok/issue status
  - IoT snapshot summary (pressure and pump_running, or "View in detail" link)
  - Navigation to detail pages via row clicks

### Detail Page with IoT (`/workorders/{id_with_iot}`)

- **Purpose:** Complete evidence chain for a work order with IoT snapshot
- **Key features:**
  - Three distinct sections: Location & Check-in, Manual Inspection Summary, IoT Evidence Record
  - Clear separation between human-reported data and machine-captured data
  - IoT Evidence Record uses table-style layout with monospaced fonts for technical values
  - Metadata-driven unit display (no hardcoded units)
  - Dual timestamp display (formatted and ISO)
  - Neutral presentation (no status interpretation, no color coding)

### Detail Page without IoT (`/workorders/{id_without_iot}`)

- **Purpose:** Work order detail when IoT snapshot is unavailable
- **Key features:**
  - Same structure as work order with IoT snapshot
  - IoT Evidence Record section shows empty state
  - Demonstrates graceful handling of missing IoT data
  - All other sections remain functional

## Technical Notes

- Backend API base URL: http://localhost:8000
- Frontend runs on: http://localhost:3000
- Database: SQLite (auto-created on first run)
- Seed data is automatically created if database is empty
- IoT snapshot metadata comes from `apps/api/config/point_meta.json`
- All data is read-only in the demo (no form submissions)

## Verifying Demo Data

To verify the demo data structure:

1. Check backend health: http://localhost:8000/health
2. Query work orders list: http://localhost:8000/api/workorders
3. Check work order with IoT: http://localhost:8000/api/workorders/1
4. Check work order without IoT: http://localhost:8000/api/workorders/5

Expected API responses:
- Work order 1: `iot_snapshot` object with `pressure`, `pump_running`, `timestamp`; `iot_snapshot_meta` object with `pressure.unit`
- Work order 5: `iot_snapshot: null`, `iot_snapshot_meta: null`

