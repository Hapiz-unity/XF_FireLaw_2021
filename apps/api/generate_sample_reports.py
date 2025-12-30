"""
Script to generate 2 sample PDF reports for demo
Run this after seeding the database
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from database import get_db, init_db
from models import WorkOrder, Location, IoTSnapshot
from services.pdf_generator import generate_pdf_report

def generate_samples():
    """Generate 2 sample reports"""
    init_db()
    db = next(get_db())
    
    try:
        # Get first 2 work orders
        work_orders = db.query(WorkOrder).limit(2).all()
        
        if len(work_orders) < 2:
            print("Error: Need at least 2 work orders. Please run seed_data first.")
            return
        
        for i, work_order in enumerate(work_orders, 1):
            location = db.query(Location).filter(Location.id == work_order.location_id).first()
            iot_snapshot = db.query(IoTSnapshot).filter(IoTSnapshot.work_order_id == work_order.id).first()
            
            if not location or not iot_snapshot:
                print(f"Error: Missing data for work order {work_order.id}")
                continue
            
            pdf_path = generate_pdf_report(work_order, location, iot_snapshot)
            print(f"Generated report {i}: {pdf_path}")
        
        print("Sample reports generated successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    generate_samples()

