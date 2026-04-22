from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis
import uuid
import os
import logging
from pydantic import BaseModel
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Processing API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Redis connection with environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    r = None

@app.options("/jobs")
def options_jobs():
    """Handle OPTIONS requests for CORS preflight"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }
    return JSONResponse(content={"message": "OPTIONS allowed"}, headers=headers)

@app.options("/jobs/{job_id}")
def options_job_by_id():
    """Handle OPTIONS requests for job by ID"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }
    return JSONResponse(content={"message": "OPTIONS allowed"}, headers=headers)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    if r is None:
        raise HTTPException(status_code=503, detail="Redis not available")
    try:
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis not available")

@app.post("/jobs")
def create_job():
    if r is None:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        job_id = str(uuid.uuid4())
        r.lpush("job", job_id)
        r.hset(f"job:{job_id}", "status", "queued")
        logger.info(f"Created job: {job_id}")
        return {"job_id": job_id}
    except redis.ConnectionError as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=503, detail="Redis connection failed")

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if r is None:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        status = r.hget(f"job:{job_id}", "status")
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"job_id": job_id, "status": status}
    except redis.ConnectionError as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=503, detail="Redis connection failed")
