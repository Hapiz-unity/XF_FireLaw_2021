"""
Seed demo data: 3 locations, 5 work orders, IoT snapshots

Demo data structure:
- Work orders 1-4: WITH IoT snapshots (for demo of evidence chain with metadata)
  * Work orders 1-2: Use LOC001 (has metadata in point_meta.json)
  * Work orders 3-4: Use LOC002 (has metadata in point_meta.json)
- Work order 5: WITHOUT IoT snapshot (for demo of null handling)
  * Uses LOC003 (has metadata, but no snapshot created)
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import Location, WorkOrder, IoTSnapshot
from services.iot import fetch_latest_snapshot

def seed_data(db: Session):
    """
    Create demo data if database is empty.
    
    Creates:
    - 3 locations (LOC001, LOC002, LOC003)
    - 5 work orders:
      * IDs 1-4: WITH IoT snapshots (evidence chain demo)
      * ID 5: WITHOUT IoT snapshot (null handling demo)
    """
    
    # Check if locations already exist
    if db.query(Location).count() > 0:
        print("Database already has data, skipping seed")
        return
    
    # Create 3 locations
    locations = [
        Location(name="消防泵房A", qr_code="LOC001"),
        Location(name="消防泵房B", qr_code="LOC002"),
        Location(name="消防泵房C", qr_code="LOC003"),
    ]
    for loc in locations:
        db.add(loc)
    db.commit()
    
    # Refresh to get IDs
    for loc in locations:
        db.refresh(loc)
    
    loc_id_to_qr = {loc.id: loc.qr_code for loc in locations}
    
    # Create 5 work orders with past dates
    now = datetime.utcnow()
    work_orders_data = [
        {
            "location_id": locations[0].id,
            "checkin_time": now - timedelta(days=5),
            "pumphouse": "ok",
            "endpoint": "ok",
            "hydrant": "ok",
            "linkage": "ok",
            "conclusion": "所有设备运行正常"
        },
        {
            "location_id": locations[0].id,
            "checkin_time": now - timedelta(days=3),
            "pumphouse": "ok",
            "endpoint": "issue",
            "hydrant": "ok",
            "linkage": "ok",
            "conclusion": "末端压力偏低，已调整"
        },
        {
            "location_id": locations[1].id,
            "checkin_time": now - timedelta(days=4),
            "pumphouse": "ok",
            "endpoint": "ok",
            "hydrant": "ok",
            "linkage": "ok",
            "conclusion": "例行检查完成"
        },
        {
            "location_id": locations[1].id,
            "checkin_time": now - timedelta(days=2),
            "pumphouse": "ok",
            "endpoint": "ok",
            "hydrant": "issue",
            "linkage": "ok",
            "conclusion": "栓头需要更换"
        },
        {
            "location_id": locations[2].id,
            "checkin_time": now - timedelta(days=1),
            "pumphouse": "ok",
            "endpoint": "ok",
            "hydrant": "ok",
            "linkage": "ok",
            "conclusion": "设备状态良好"
        },
    ]
    
    for idx, wo_data in enumerate(work_orders_data):
        work_order = WorkOrder(**wo_data)
        db.add(work_order)
        db.flush()  # Get work_order.id
        
        # Demo data: Skip IoT snapshot creation for the last work order (ID 5)
        # This provides a demo case for null handling in the UI
        is_last_work_order = (idx == len(work_orders_data) - 1)
        
        if not is_last_work_order:
            # Create IoT snapshot for work orders 1-4 (evidence chain demo)
            point_id = loc_id_to_qr.get(wo_data["location_id"], f"LOC{wo_data['location_id']:03d}")
            iot_data = fetch_latest_snapshot(point_id)
            
            # Ensure iot_data is a dict, treat as empty dict if not
            if not isinstance(iot_data, dict):
                iot_data = {}
            
            # Extract pump_running (boolean) from IoT payload, with fallback
            if "pump_running" in iot_data:
                pump_running = bool(iot_data["pump_running"])
            elif "pump_status" in iot_data:
                # Fallback: convert string status to boolean
                pump_running = iot_data["pump_status"].lower() in ["running", "true", "1"]
            else:
                # Default fallback
                pump_running = True
            
            # Extract timestamp with safe fallback
            if "timestamp" in iot_data and iot_data["timestamp"]:
                try:
                    timestamp_str = iot_data["timestamp"].replace("Z", "+00:00")
                    timestamp = datetime.fromisoformat(timestamp_str)
                except (ValueError, AttributeError):
                    # Fallback to current time if timestamp parsing fails
                    timestamp = datetime.utcnow()
            else:
                # Fallback to current time if timestamp is missing
                timestamp = datetime.utcnow()

            # Safe numeric parsing for pressure with fallback
            pressure_raw = iot_data.get("pressure") if isinstance(iot_data, dict) else None
            try:
                pressure_value = float(pressure_raw) if pressure_raw is not None else 0.0
            except (TypeError, ValueError):
                pressure_value = 0.0
            
            iot_snapshot = IoTSnapshot(
                work_order_id=work_order.id,
                pressure=pressure_value,
                pump_running=pump_running,  # Boolean field
                timestamp=timestamp
            )
            db.add(iot_snapshot)
        # else: Work order 5 has no IoT snapshot (null handling demo)
    
    db.commit()
    print(f"Seeded {len(locations)} locations and {len(work_orders_data)} work orders")
