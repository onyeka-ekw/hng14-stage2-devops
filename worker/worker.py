import redis
import time
import os
import signal
import logging
import sys
from threading import Event

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
PROCESSING_TIME = int(os.getenv("PROCESSING_TIME", 2))

# Graceful shutdown event
shutdown_event = Event()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown_event.set()

def process_job(job_id, r):
    """Process a single job"""
    try:
        logger.info(f"Processing job {job_id}")
        
        # Update status to processing
        r.hset(f"job:{job_id}", "status", "processing")
        
        # Simulate work with configurable time
        time.sleep(PROCESSING_TIME)
        
        # Update status to completed
        r.hset(f"job:{job_id}", "status", "completed")
        logger.info(f"Completed job {job_id}")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        r.hset(f"job:{job_id}", "status", "failed")

def main():
    """Main worker loop"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Connect to Redis
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)
    
    logger.info("Worker started, waiting for jobs...")
    
    # Main loop
    while not shutdown_event.is_set():
        try:
            job = r.brpop("job", timeout=5)
            if job:
                _, job_id = job
                process_job(job_id, r)
            else:
                # Timeout occurred, check shutdown flag
                continue
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            # Wait before retrying
            time.sleep(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(1)
    
    logger.info("Worker shutting down")

if __name__ == "__main__":
    main()