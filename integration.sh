#!/bin/bash
set -e

echo "Running integration tests..."

# Wait for services to be ready with timeout
echo "Waiting for services to be healthy..."
timeout 300 bash -c 'until curl -f http://localhost:3000/health; do sleep 5; done'
timeout 300 bash -c 'until curl -f http://localhost:8000/health; do sleep 5; done'

echo "Services are healthy, running tests..."

# Submit a job
job_response=$(curl -s -X POST http://localhost:3000/submit)
job_id=$(echo $job_response | jq -r '.job_id')

if [ -z "$job_id" ] || [ "$job_id" = "null" ]; then
    echo "Failed to submit job"
    exit 1
fi

echo "Job submitted: $job_id"

# Poll for job completion with timeout
timeout 120 bash -c '
    for i in {1..60}; do
        status_response=$(curl -s http://localhost:3000/status/'$job_id')
        status=$(echo $status_response | jq -r ".status")
        
        echo "Job status: $status"
        
        if [ "$status" = "completed" ]; then
            echo "Job completed successfully"
            exit 0
        fi
        
        if [ "$status" = "failed" ]; then
            echo "Job failed"
            exit 1
        fi
        
        sleep 2
    done
    echo "Timeout waiting for job completion"
    exit 1
'

echo "Integration tests passed!"
