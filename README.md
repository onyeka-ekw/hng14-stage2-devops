# TASK TWO

A production-ready multi-service job processing application with Redis queue, FastAPI backend, Node.js frontend, and Python worker.

## Architecture

- **Frontend** (Node.js/Express): User interface for submitting and tracking jobs
- **API** (Python/FastAPI): REST API for job creation and status retrieval
- **Worker** (Python): Background job processor
- **Redis**: Message queue and job state storage

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.12+ (for local development)
- Redis server (for local development)

## Quick Start with Docker

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd hng14-stage2-devops
   cp .env.example .env
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Verify deployment**
   ```bash
   # Check health of services
   curl http://localhost:3000/health  # Frontend
   curl http://localhost:8000/health  # API
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Local Development Setup

### 1. Start Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Setup API
```bash
cd api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Setup Worker
```bash
cd worker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python worker.py
```

### 4. Setup Frontend
```bash
cd frontend
npm install
npm start
```

### 5. Test the Application
1. Open http://localhost:3000
2. Click "Submit New Job"
3. Watch the job progress from "queued" to "processing" to "completed"

## Environment Variables

Copy `.env.example` to `.env` and configure as needed:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | localhost | Redis server host |
| `REDIS_PORT` | 6379 | Redis server port |
| `API_URL` | http://localhost:8000 | Frontend API endpoint |
| `FRONTEND_PORT` | 3000 | Frontend port |
| `PROCESSING_TIME` | 2 | Worker processing time (seconds) |

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Job Management
- `POST /jobs` - Create a new job
- `GET /jobs/{job_id}` - Get job status

### Frontend Endpoints
- `GET /health` - Frontend health check
- `POST /submit` - Submit job (proxies to API)
- `GET /status/{id}` - Get job status (proxies to API)

## Testing

### Unit Tests
```bash
cd api
pytest --cov=. --cov-report=html
```

### Integration Tests
```bash
# With Docker Compose
docker-compose up -d
./scripts/integration-test.sh
docker-compose down
```

## CI/CD Pipeline

The application includes a complete CI/CD pipeline using GitHub Actions:

1. **Lint** - Python (flake8), JavaScript (eslint), Dockerfiles (hadolint)
2. **Test** - Unit tests with coverage reporting
3. **Build** - Multi-stage Docker builds with SHA tagging
4. **Security Scan** - Trivy vulnerability scanning
5. **Integration Test** - Full stack testing
6. **Deploy** - Rolling updates on main branch

Pipeline triggers:
- Push to `main` or `develop` branches
- Pull requests to `main`

## Production Deployment

### Docker Compose Production
```bash
# Production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Health Checks
All services include health checks:
- Frontend: `/health` endpoint
- API: `/health` endpoint with Redis connectivity
- Worker: Process health verification
- Redis: `redis-cli ping`

### Monitoring
- Container health status via `docker ps`
- Application logs via `docker-compose logs`
- Redis monitoring via `redis-cli INFO`

## Security Features

- Non-root container users
- Security headers (helmet.js)
- CORS configuration
- No secrets in images
- Environment-based configuration
- Resource limits in Docker Compose

## Troubleshooting

### Common Issues

1. **Redis connection refused**
   ```bash
   # Check Redis status
   sudo systemctl status redis-server
   # Or with Docker
   docker ps | grep redis
   ```

2. **Port conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :8000
   ```

3. **Container health checks failing**
   ```bash
   # Check container logs
   docker-compose logs api
   docker-compose logs frontend
   ```

### Reset Environment
```bash
# Stop all services
docker-compose down -v

# Remove containers and images
docker system prune -a

# Restart
docker-compose up -d
```

## Development Workflow

1. Make changes to code
2. Run tests locally
3. Commit changes
4. CI/CD pipeline runs automatically
5. Deploy to production on main branch merge

## Performance Considerations

- API and worker use Redis connection pooling
- Frontend includes proper error handling
- Docker containers have resource limits
- Health checks prevent cascade failures

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes and add tests
4. Ensure CI/CD pipeline passes
5. Submit pull request

## License

This project is part of HNG Stage 2 DevOps assessment.
