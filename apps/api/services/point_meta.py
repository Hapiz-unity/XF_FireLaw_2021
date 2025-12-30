"""
Point metadata loader with in-memory caching
Loads point_meta.json and provides metric metadata lookup
"""
import json
from pathlib import Path
from typing import Dict, Optional

# Module-level cache
_metadata_cache: Optional[Dict] = None

def _load_metadata() -> Dict:
    """Load point metadata from JSON file, with fallback on error"""
    global _metadata_cache
    
    if _metadata_cache is not None:
        return _metadata_cache
    
    config_path = Path(__file__).parent.parent / "config" / "point_meta.json"
    
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                _metadata_cache = json.load(f)
                return _metadata_cache
    except (json.JSONDecodeError, IOError, OSError):
        pass
    
    # Fallback: empty dict
    _metadata_cache = {}
    return _metadata_cache

def get_metric_meta(point_id: Optional[str], metric_key: str) -> Dict[str, Optional[str]]:
    """
    Get metric metadata for a given point and metric key
    
    Args:
        point_id: Point identifier (e.g., "LOC001") or None
        metric_key: Metric key (e.g., "pressure", "flow", "current")
    
    Returns:
        Dict with "unit" and "unit_source" keys
        Fallback: {"unit": None, "unit_source": "unknown"}
    """
    if not point_id:
        return {"unit": None, "unit_source": "unknown"}
    
    metadata = _load_metadata()
    
    try:
        point_data = metadata.get(point_id, {})
        metrics = point_data.get("metrics", {})
        metric_meta = metrics.get(metric_key, {})
        
        return {
            "unit": metric_meta.get("unit"),
            "unit_source": metric_meta.get("unit_source", "unknown")
        }
    except (AttributeError, KeyError, TypeError):
        return {"unit": None, "unit_source": "unknown"}

