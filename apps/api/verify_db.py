#!/usr/bin/env python3
"""
Verification script for database reset
Shows the exact commands and expected output
"""
import os
import sys
import subprocess
import json

def verify_backend_and_api():
    """Verify backend is running and API returns correct structure"""
    
    print("=" * 60)
    print("VERIFICATION: Backend API Response")
    print("=" * 60)
    print()
    
    # Step 1: Get a work order ID
    print("Step 1: Get work order list")
    print("Command: curl -s http://localhost:8000/api/workorders")
    print()
    
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8000/api/workorders"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"✗ Error: {result.stderr}")
            return None
        
        work_orders = json.loads(result.stdout)
        if not work_orders:
            print("✗ No work orders found")
            return None
        
        work_order_id = work_orders[0]['id']
        print(f"✓ Found work order ID: {work_order_id}")
        print()
        
        # Step 2: Get work order detail
        print("Step 2: Get work order detail")
        print(f"Command: curl -s \"http://localhost:8000/api/workorders/{work_order_id}\"")
        print()
        
        result = subprocess.run(
            [f"curl", "-s", f"http://localhost:8000/api/workorders/{work_order_id}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"✗ Error: {result.stderr}")
            return None
        
        work_order = json.loads(result.stdout)
        
        print("Response:")
        print(json.dumps(work_order, indent=2, ensure_ascii=False))
        print()
        
        # Step 3: Verify structure
        print("=" * 60)
        print("VERIFICATION RESULTS")
        print("=" * 60)
        
        if 'iot_snapshot' in work_order and work_order['iot_snapshot']:
            iot = work_order['iot_snapshot']
            
            has_pump_running = 'pump_running' in iot
            has_pump_status = 'pump_status' in iot
            pump_running_val = iot.get('pump_running')
            is_boolean = isinstance(pump_running_val, bool)
            
            print(f"✓ Contains 'pump_running': {has_pump_running}")
            if has_pump_running:
                print(f"  Value: {pump_running_val}")
                print(f"  Type: {type(pump_running_val).__name__}")
                print(f"  Is boolean: {is_boolean}")
            print(f"✓ Does NOT contain 'pump_status': {not has_pump_status}")
            
            if has_pump_running and is_boolean and not has_pump_status:
                print()
                print("✅ API Response Verification: PASSED")
            else:
                print()
                print("✗ API Response Verification: FAILED")
        else:
            print("✗ No IoT snapshot in response")
        
        return work_order_id
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error: {e}")
        print(f"Response was: {result.stdout[:200]}")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def verify_sqlite_schema():
    """Verify SQLite database schema"""
    
    print()
    print("=" * 60)
    print("VERIFICATION: SQLite Schema")
    print("=" * 60)
    print()
    
    db_path = './data/app.db'
    
    if not os.path.exists(db_path):
        print(f"✗ Database file not found: {db_path}")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Database: {os.path.abspath(db_path)}")
        print()
        
        cursor.execute('PRAGMA table_info(iot_snapshots)')
        columns = cursor.fetchall()
        
        print("iot_snapshots table columns:")
        col_names = []
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_names.append(col_name)
            marker = '✓' if col_name == 'pump_running' else ('✗' if col_name == 'pump_status' else ' ')
            print(f"  {marker} {col_name}: {col_type}")
        
        print()
        has_pump_running = 'pump_running' in col_names
        has_pump_status = 'pump_status' in col_names
        
        print("Verification:")
        print(f"  ✓ pump_running exists: {has_pump_running}")
        print(f"  ✓ pump_status removed: {not has_pump_status}")
        
        # Check sample data
        cursor.execute('SELECT id, pressure, pump_running FROM iot_snapshots LIMIT 1')
        row = cursor.fetchone()
        if row:
            print(f"  Sample data: id={row[0]}, pressure={row[1]}, pump_running={row[2]} (type: {type(row[2]).__name__})")
        
        conn.close()
        
        if has_pump_running and not has_pump_status:
            print()
            print("✅ Schema Verification: PASSED")
            return True
        else:
            print()
            print("✗ Schema Verification: FAILED")
            return False
            
    except ImportError:
        print("✗ sqlite3 module not available")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Database Reset Verification")
    print("=" * 60)
    print()
    
    # Check if backend is running
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8000/health"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode != 0:
            print("✗ Backend is not running")
            print("  Please start the backend first: python3 main.py")
            sys.exit(1)
    except Exception:
        print("✗ Backend is not running")
        print("  Please start the backend first: python3 main.py")
        sys.exit(1)
    
    # Verify API
    work_order_id = verify_backend_and_api()
    
    # Verify schema
    schema_ok = verify_sqlite_schema()
    
    print()
    print("=" * 60)
    if work_order_id and schema_ok:
        print("✅ ALL VERIFICATIONS PASSED")
    else:
        print("✗ SOME VERIFICATIONS FAILED")
    print("=" * 60)

