from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from database import init_db, get_db
from routers import checkin, workorders, reports
from seed_data import seed_data

app = FastAPI(title="Fire Pump Maintenance MVP API")

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(checkin.router)
app.include_router(workorders.router)
app.include_router(reports.router)

# Serve uploaded files
upload_dir = os.getenv("UPLOAD_DIR", "./data/uploads")
Path(upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Seed data if database is empty
    db = next(get_db())
    try:
        seed_data(db)
    finally:
        db.close()

@app.get("/health")
def health_check():
    import json
    import time
    log_path = "/Users/haipei/Desktop/消防/Legal_DB/02_Laws/XF_FireLaw_2021/.cursor/debug.log"
    # #region agent log
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"main.py:44","message":"health check called","data":{"endpoint":"/health"},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
    # #endregion
    return {"status": "ok"}

@app.get("/")
def root():
    import json
    import time
    log_path = "/Users/haipei/Desktop/消防/Legal_DB/02_Laws/XF_FireLaw_2021/.cursor/debug.log"
    # #region agent log
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"main.py:52","message":"root endpoint called","data":{"endpoint":"/"},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
    # #endregion
    return {"message": "Fire Pump Maintenance MVP API", "docs": "/docs", "health": "/health"}

if __name__ == "__main__":
    import uvicorn
    import json
    import time
    log_path = "/Users/haipei/Desktop/消防/Legal_DB/02_Laws/XF_FireLaw_2021/.cursor/debug.log"
    port = int(os.getenv("API_PORT", 8000))
    # #region agent log
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"location":"main.py:48","message":"backend startup attempt","data":{"port":port,"host":"0.0.0.0"},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
    # #endregion
    try:
        # #region agent log
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"main.py:52","message":"uvicorn.run called","data":{"port":port},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
        # #endregion
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        # #region agent log
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"location":"main.py:56","message":"backend startup failed","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+"\n")
        # #endregion
        raise

