from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
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
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create work order check-in with form fields and auto-bind IoT snapshot
    Fields must match fields_mvp.csv exactly
    """
    # Parse form data manually
    form = await request.form()
    location_id = int(form.get("location_id"))
    pumphouse = form.get("pumphouse")
    endpoint = form.get("endpoint")
    hydrant = form.get("hydrant")
    linkage = form.get("linkage")
    conclusion = form.get("conclusion")
    photo = form.get("photo")
    
    import json
    log_path = "/Users/haipei/Desktop/消防/Legal_DB/02_Laws/XF_FireLaw_2021/.cursor/debug.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"routers/checkin.py:34","message":"create_checkin entry","data":{"location_id":location_id,"pumphouse":pumphouse,"endpoint":endpoint,"hydrant":hydrant,"linkage":linkage,"has_conclusion":conclusion is not None,"has_photo":photo is not None},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
    
    # Validate location exists
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"routers/checkin.py:52","message":"location not found","data":{"location_id":location_id},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Validate field values (正常/异常 for select fields)
    valid_statuses = ["正常", "异常"]
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"routers/checkin.py:56","message":"before field validation","data":{"pumphouse":pumphouse,"endpoint":endpoint,"hydrant":hydrant,"linkage":linkage,"valid_statuses":valid_statuses},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
    if pumphouse not in valid_statuses:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"routers/checkin.py:57","message":"pumphouse validation failed","data":{"pumphouse":pumphouse,"valid_statuses":valid_statuses},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
        raise HTTPException(status_code=400, detail="pumphouse must be 正常 or 异常")
    if endpoint not in valid_statuses:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"routers/checkin.py:59","message":"endpoint validation failed","data":{"endpoint":endpoint,"valid_statuses":valid_statuses},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
        raise HTTPException(status_code=400, detail="endpoint must be 正常 or 异常")
    if hydrant not in valid_statuses:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"routers/checkin.py:61","message":"hydrant validation failed","data":{"hydrant":hydrant,"valid_statuses":valid_statuses},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
        raise HTTPException(status_code=400, detail="hydrant must be 正常 or 异常")
    if linkage not in valid_statuses:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"routers/checkin.py:63","message":"linkage validation failed","data":{"linkage":linkage,"valid_statuses":valid_statuses},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
        raise HTTPException(status_code=400, detail="linkage must be 正常 or 异常")
    
    # Handle photo upload
    photo_path = None
    if photo and isinstance(photo, UploadFile):
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
    import json
    log_path = "/Users/haipei/Desktop/消防/Legal_DB/02_Laws/XF_FireLaw_2021/.cursor/debug.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"routers/checkin.py:95","message":"iot_data fetched","data":{"iot_data_keys":list(iot_data.keys()),"has_pump_running":"pump_running" in iot_data,"has_pump_status":"pump_status" in iot_data},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
    
    # Handle pump_running (boolean) with fallback for compatibility
    pump_running = False
    if "pump_running" in iot_data:
        pump_running = bool(iot_data["pump_running"])
    elif "pump_status" in iot_data:
        # Fallback: convert string status to boolean
        pump_running = str(iot_data["pump_status"]).lower() in ["running", "true", "1"]
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"routers/checkin.py:109","message":"before creating iot_snapshot","data":{"work_order_id":work_order.id,"pressure":iot_data["pressure"],"pump_running":pump_running},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
    
    # Create IoT snapshot
    try:
        iot_snapshot = IoTSnapshot(
            work_order_id=work_order.id,
            pressure=iot_data["pressure"],
            pump_running=pump_running,  # Boolean field
            timestamp=datetime.fromisoformat(iot_data["timestamp"].replace("Z", "+00:00"))
        )
        db.add(iot_snapshot)
        db.commit()
        db.refresh(work_order)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"routers/checkin.py:120","message":"iot_snapshot created successfully","data":{"work_order_id":work_order.id,"iot_snapshot_id":iot_snapshot.id},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
    except Exception as e:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"routers/checkin.py:122","message":"iot_snapshot creation failed","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+"\n")
        raise
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"routers/checkin.py:125","message":"create_checkin success","data":{"work_order_id":work_order.id},"timestamp":int(__import__("time").time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+"\n")
    
    return {
        "work_order_id": work_order.id,
        "message": "Check-in created successfully",
        "iot_snapshot": {
            "pressure": iot_snapshot.pressure,
            "pump_running": iot_snapshot.pump_running  # Boolean field
        }
    }

