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
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

