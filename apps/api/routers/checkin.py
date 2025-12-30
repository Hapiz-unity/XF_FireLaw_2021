from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import os
from pathlib import Path
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_db
from models import Location, WorkOrder, IoTSnapshot
from services.iot import fetch_latest_snapshot

router = APIRouter(prefix="/api", tags=["checkin"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")

@router.get("/locations")
def list_locations(db: Session = Depends(get_db)):
    """List all locations for dropdown selection"""
    locations = db.query(Location).all()
    return [{"id": loc.id, "name": loc.name, "qr_code": loc.qr_code} for loc in locations]

@router.get("/locations/qr/{qr_code}")
def get_location_by_qr(qr_code: str, db: Session = Depends(get_db)):
    """Get location by QR code"""
    location = db.query(Location).filter(Location.qr_code == qr_code).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"id": location.id, "name": location.name, "qr_code": location.qr_code}

@router.post("/checkin")
async def create_checkin(
    location_id: int,
    pumphouse: str,
    endpoint: str,
    hydrant: str,
    linkage: str,
    conclusion: Optional[str] = None,
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create work order check-in with form fields and auto-bind IoT snapshot
    Fields must match fields_mvp.csv exactly
    """
    # Validate location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Validate field values (正常/异常 for select fields)
    valid_statuses = ["正常", "异常"]
    if pumphouse not in valid_statuses:
        raise HTTPException(status_code=400, detail="pumphouse must be 正常 or 异常")
    if endpoint not in valid_statuses:
        raise HTTPException(status_code=400, detail="endpoint must be 正常 or 异常")
    if hydrant not in valid_statuses:
        raise HTTPException(status_code=400, detail="hydrant must be 正常 or 异常")
    if linkage not in valid_statuses:
        raise HTTPException(status_code=400, detail="linkage must be 正常 or 异常")
    
    # Handle photo upload
    photo_path = None
    if photo:
        Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        file_extension = os.path.splitext(photo.filename)[1] if photo.filename else ".jpg"
        photo_filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        photo_full_path = os.path.join(UPLOAD_DIR, photo_filename)
        
        with open(photo_full_path, "wb") as f:
            content = await photo.read()
            f.write(content)
        
        # Store only filename for serving via /uploads endpoint
        photo_path = photo_filename
    
    # Create work order
    work_order = WorkOrder(
        location_id=location_id,
        checkin_time=datetime.utcnow(),
        pumphouse=pumphouse,
        endpoint=endpoint,
        hydrant=hydrant,
        linkage=linkage,
        conclusion=conclusion,
        photo_path=photo_path
    )
    db.add(work_order)
    db.flush()  # Get work_order.id
    
    # Auto-fetch IoT snapshot
    iot_data = fetch_latest_snapshot(f"pump_{location_id}")
    
    # Create IoT snapshot
    iot_snapshot = IoTSnapshot(
        work_order_id=work_order.id,
        pressure=iot_data["pressure"],
        pump_status=iot_data["pump_status"],
        timestamp=datetime.fromisoformat(iot_data["timestamp"].replace("Z", "+00:00"))
    )
    db.add(iot_snapshot)
    db.commit()
    db.refresh(work_order)
    
    return {
        "work_order_id": work_order.id,
        "message": "Check-in created successfully",
        "iot_snapshot": {
            "pressure": iot_snapshot.pressure,
            "pump_status": iot_snapshot.pump_status
        }
    }

