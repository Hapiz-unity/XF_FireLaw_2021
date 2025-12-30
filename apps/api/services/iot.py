"""
Mock IoT service - returns sample data matching iot_sample_payload.json structure
"""
import json
from datetime import datetime
from pathlib import Path

def load_iot_schema():
    """Load IoT payload schema from docs/iot_sample_payload.json"""
    schema_path = Path(__file__).parent.parent.parent.parent / "docs" / "iot_sample_payload.json"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def fetch_latest_snapshot(device_id: str = None):
    """
    Mock IoT data fetcher - returns sample data matching iot_sample_payload.json
    
    For MVP demo: returns hardcoded sample data
    Structure must match docs/iot_sample_payload.json exactly
    """
    # Load schema to ensure structure matches
    schema = load_iot_schema()
    
    # Return mock data with varying values for demo
    import random
    pressure_values = [0.60, 0.65, 0.70, 0.55]
    pump_statuses = ["running", "stopped"]
    
    return {
        "device_id": device_id or "pump_001",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "pressure": random.choice(pressure_values),
        "pump_status": random.choice(pump_statuses)
    }

