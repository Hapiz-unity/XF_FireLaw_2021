from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from database import get_db
from models import WorkOrder, Location, IoTSnapshot
from services.pdf_generator import generate_pdf_report

router = APIRouter(prefix="/api", tags=["reports"])

@router.post("/reports/generate")
def generate_report(work_order_id: int = Form(...), db: Session = Depends(get_db)):
    """
    Generate PDF report for a work order and save to 04_output/demo_report_samples/
    """
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    location = db.query(Location).filter(Location.id == work_order.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    iot_snapshot = db.query(IoTSnapshot).filter(IoTSnapshot.work_order_id == work_order_id).first()
    if not iot_snapshot:
        raise HTTPException(status_code=404, detail="IoT snapshot not found")
    
    # Generate PDF
    pdf_path = generate_pdf_report(work_order, location, iot_snapshot)
    
    return {
        "work_order_id": work_order_id,
        "pdf_path": pdf_path,
        "message": "Report generated successfully"
    }

