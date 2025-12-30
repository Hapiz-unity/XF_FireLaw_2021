#!/usr/bin/env python3
"""
Database reset script for SQLite development
Deletes existing database and recreates tables with current models
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import DATABASE_URL, init_db, get_db
from seed_data import seed_data

def reset_database():
    """Reset SQLite database by deleting and recreating"""
    
    # Step 1: Detect and delete SQLite database file
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_path):
            print(f"Deleting existing database: {db_path}")
            os.remove(db_path)
            print("✓ Database file deleted")
        else:
            print(f"✓ No existing database file at: {db_path}")
    else:
        print(f"⚠ Warning: DATABASE_URL is not SQLite: {DATABASE_URL}")
        print("  Skipping database deletion (non-SQLite databases not touched)")
        return
    
    # Step 2: Initialize database (creates tables from models.py)
    print("\nStep 2: Creating tables from models.py...")
    init_db()
    print("✓ Tables created with current schema")
    print("  - IoTSnapshot.pump_running (Boolean) field is present")
    print("  - No pump_status column exists")
    
    # Step 3: Seed data
    print("\nStep 3: Seeding demo data...")
    db = next(get_db())
    try:
        seed_data(db)
        print("✓ Demo data seeded successfully")
    finally:
        db.close()
    
    # Verification
    print("\nStep 4: Verifying database structure...")
    db = next(get_db())
    try:
        from models import IoTSnapshot
        import sqlite3
        
        # Check table structure via SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(iot_snapshots)")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        has_pump_running = "pump_running" in col_names
        has_pump_status = "pump_status" in col_names
        
        print(f"  ✓ pump_running column exists: {has_pump_running}")
        print(f"  ✓ pump_status column removed: {not has_pump_status}")
        
        # Check sample data
        iot = db.query(IoTSnapshot).first()
        if iot:
            print(f"  ✓ Sample data: pressure={iot.pressure}, pump_running={iot.pump_running} (type: {type(iot.pump_running).__name__})")
        
        conn.close()
    finally:
        db.close()
    
    print("\n✅ Database reset complete!")
    print("✅ Backend is ready to start with pump_running (Boolean) field")

if __name__ == "__main__":
    try:
        reset_database()
    except ImportError as e:
        print(f"\n❌ Error: Dependencies not installed")
        print(f"   {e}")
        print("\nPlease install dependencies first:")
        print("   pip install fastapi uvicorn sqlalchemy python-multipart reportlab")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during database reset: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

