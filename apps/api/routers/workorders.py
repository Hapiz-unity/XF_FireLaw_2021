from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_db
from models import WorkOrder, Location, IoTSnapshot
from services.point_meta import get_metric_meta

router = APIRouter(prefix="/api", tags=["workorders"])

@router.get("/workorders")
def query_work_orders(
    date_from: Optional[str] = Query(None, alias="date_from"),
    date_to: Optional[str] = Query(None, alias="date_to"),
    location_id: Optional[int] = Query(None, alias="location_id"),
    db: Session = Depends(get_db)
):
    """
    Query work orders with filters: date_from, date_to, location_id
    """
    query = db.query(WorkOrder)
    
    # Apply filters
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
            query = query.filter(WorkOrder.checkin_time >= date_from_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format (use ISO format)")
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
            query = query.filter(WorkOrder.checkin_time <= date_to_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format (use ISO format)")
    
    if location_id:
        query = query.filter(WorkOrder.location_id == location_id)
    
    work_orders = query.order_by(WorkOrder.checkin_time.desc()).all()
    
    result = []
    for wo in work_orders:
        location = db.query(Location).filter(Location.id == wo.location_id).first()
        result.append({
            "id": wo.id,
            "location_id": wo.location_id,
            "location_name": location.name if location else None,
            "checkin_time": wo.checkin_time.isoformat(),
            "pumphouse": wo.pumphouse,
            "endpoint": wo.endpoint,
            "hydrant": wo.hydrant,
            "linkage": wo.linkage,
            "conclusion": wo.conclusion,
            "created_at": wo.created_at.isoformat()
        })
    
    return result

@router.get("/workorders/{work_order_id}")
def get_work_order_detail(work_order_id: int, db: Session = Depends(get_db)):
    """
    Get work order details with IoT snapshot
    """
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    location = db.query(Location).filter(Location.id == work_order.location_id).first()
    iot_snapshot = db.query(IoTSnapshot).filter(IoTSnapshot.work_order_id == work_order_id).first()
    
    # Determine point_id from location QR code
    point_id = location.qr_code if location else None
    
    # Build IoT snapshot with metadata
    # Evidence-chain semantics: iot_snapshot = null => iot_snapshot_meta = null
    # (not {} - empty object would imply metadata exists but is empty, which is incorrect)
    iot_snapshot_data = None
    iot_snapshot_meta = None
    
    if iot_snapshot:
        iot_snapshot_data = {
            "pressure": iot_snapshot.pressure,
            "pump_running": iot_snapshot.pump_running,
            "timestamp": iot_snapshot.timestamp.isoformat()
        }
        
        # Attach metadata only for metrics that exist in iot_snapshot
        # Skip pump_running (boolean, no unit) and timestamp (datetime, no unit)
        # See docs/EVIDENCE_CHAIN_CONTRACT_MVP.md for semantics
        iot_snapshot_meta = {}
        if iot_snapshot.pressure is not None:
            iot_snapshot_meta["pressure"] = get_metric_meta(point_id, "pressure")
        
        # Future metrics (flow, current) would be added here if they exist in the model
        # Example:
        # if hasattr(iot_snapshot, "flow") and iot_snapshot.flow is not None:
        #     iot_snapshot_meta["flow"] = get_metric_meta(point_id, "flow")
    
    result = {
        "id": work_order.id,
        "location": {
            "id": location.id,
            "name": location.name,
            "qr_code": location.qr_code
        } if location else None,
        "checkin_time": work_order.checkin_time.isoformat(),
        "pumphouse": work_order.pumphouse,
        "endpoint": work_order.endpoint,
        "hydrant": work_order.hydrant,
        "linkage": work_order.linkage,
        "conclusion": work_order.conclusion,
        "photo_path": work_order.photo_path,
        "created_at": work_order.created_at.isoformat(),
        "iot_snapshot": iot_snapshot_data,
        "iot_snapshot_meta": iot_snapshot_meta
    }
    
    return result

