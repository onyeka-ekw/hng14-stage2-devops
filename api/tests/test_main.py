import pytest
from unittest.mock import Mock, patch
import redis
import uuid
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

@pytest.fixture
def mock_redis():
    """Mock Redis connection"""
    with patch('main.r') as mock_redis:
        mock_redis.ping.return_value = True
        mock_redis.decode_responses = True
        yield mock_redis

@pytest.fixture
def mock_redis_connection_error():
    """Mock Redis connection error"""
    with patch('main.r', None):
        yield

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_healthy(self, mock_redis):
        """Test health check when Redis is available"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "redis": "connected"}
    
    def test_health_check_redis_unavailable(self, mock_redis_connection_error):
        """Test health check when Redis is not available"""
        response = client.get("/health")
        assert response.status_code == 503
        assert "Redis not available" in response.json()["detail"]

class TestCreateJob:
    """Test job creation endpoint"""
    
    def test_create_job_success(self, mock_redis):
        """Test successful job creation"""
        # Mock UUID generation
        with patch('main.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
            
            response = client.post("/jobs")
            
            assert response.status_code == 200
            assert response.json() == {"job_id": "12345678-1234-5678-1234-567812345678"}
            
            # Verify Redis operations were called
            mock_redis.lpush.assert_called_once_with("job", "12345678-1234-5678-1234-567812345678")
            mock_redis.hset.assert_called_once_with("job:12345678-1234-5678-1234-567812345678", "status", "queued")
    
    def test_create_job_redis_unavailable(self, mock_redis_connection_error):
        """Test job creation when Redis is not available"""
        response = client.post("/jobs")
        assert response.status_code == 503
        assert "Redis not available" in response.json()["detail"]
    
    def test_create_job_redis_connection_error(self, mock_redis):
        """Test job creation when Redis connection fails"""
        mock_redis.lpush.side_effect = redis.ConnectionError("Connection failed")
        
        response = client.post("/jobs")
        assert response.status_code == 503
        assert "Redis connection failed" in response.json()["detail"]

class TestGetJob:
    """Test job status endpoint"""
    
    def test_get_job_success(self, mock_redis):
        """Test successful job status retrieval"""
        mock_redis.hget.return_value = "completed"
        
        response = client.get("/jobs/test-job-id")
        
        assert response.status_code == 200
        assert response.json() == {"job_id": "test-job-id", "status": "completed"}
        mock_redis.hget.assert_called_once_with("job:test-job-id", "status")
    
    def test_get_job_not_found(self, mock_redis):
        """Test job status when job doesn't exist"""
        mock_redis.hget.return_value = None
        
        response = client.get("/jobs/nonexistent-job")
        
        assert response.status_code == 404
        assert "Job not found" in response.json()["detail"]
    
    def test_get_job_redis_unavailable(self, mock_redis_connection_error):
        """Test job status when Redis is not available"""
        response = client.get("/jobs/test-job-id")
        assert response.status_code == 503
        assert "Redis not available" in response.json()["detail"]
    
    def test_get_job_redis_connection_error(self, mock_redis):
        """Test job status when Redis connection fails"""
        mock_redis.hget.side_effect = redis.ConnectionError("Connection failed")
        
        response = client.get("/jobs/test-job-id")
        assert response.status_code == 503
        assert "Redis connection failed" in response.json()["detail"]

class TestCORS:
    """Test CORS middleware"""
    
    def test_cors_headers(self, mock_redis):
        """Test CORS headers are present"""
        response = client.options("/jobs")
        assert "access-control-allow-origin" in response.headers

class TestIntegration:
    """Integration tests"""
    
    def test_full_job_lifecycle(self, mock_redis):
        """Test complete job lifecycle"""
        # Mock UUID generation
        with patch('main.uuid.uuid4') as mock_uuid:
            job_id = "12345678-1234-5678-1234-567812345678"
            mock_uuid.return_value = uuid.UUID(job_id)
            
            # Create job
            create_response = client.post("/jobs")
            assert create_response.status_code == 200
            assert create_response.json()["job_id"] == job_id
            
            # Mock job status as queued
            mock_redis.hget.return_value = "queued"
            
            # Check job status
            status_response = client.get(f"/jobs/{job_id}")
            assert status_response.status_code == 200
            assert status_response.json()["status"] == "queued"
            
            # Mock job status as completed
            mock_redis.hget.return_value = "completed"
            
            # Check final status
            final_response = client.get(f"/jobs/{job_id}")
            assert final_response.status_code == 200
            assert final_response.json()["status"] == "completed"
