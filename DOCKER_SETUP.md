# Docker Setup Guide - Motor Biomecânico

This guide covers setting up and running the Motor Biomecânico application using Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Development Setup](#development-setup)
4. [Production Setup](#production-setup)
5. [Common Commands](#common-commands)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Docker**: v20.10 or higher
- **Docker Compose**: v2.0 or higher

### Installation

**On macOS and Windows:**
- Download [Docker Desktop](https://www.docker.com/products/docker-desktop)

**On Linux:**
```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Add current user to docker group (optional, avoids sudo)
sudo usermod -aG docker $USER
newgrp docker
```

## Quick Start

### Production Mode (Recommended for deployment)

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api
```

### Verify Services

```bash
# Check service status
docker-compose ps

# Test backend health
curl http://localhost:8000/api/health

# Test frontend (should return HTML)
curl http://localhost:3000
```

## Development Setup

For development with hot reload:

```bash
# Start services with development overlay
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Frontend will be available at http://localhost:5173 (Vite dev server)
# Backend at http://localhost:8000/api with auto-reload on code changes
```

### Key Features

- **Frontend Hot Module Replacement (HMR)**: Changes to React code are instantly reflected
- **Backend Auto-reload**: Backend restarts automatically when Python files change
- **Volume Mounts**: Code is mounted as volumes for live editing
- **Network Integration**: Services communicate over isolated network

## Production Setup

### Build Images Only

```bash
# Build without starting
docker-compose build

# View built images
docker images | grep motor-biomecanico
```

### Run Production Container

```bash
# Start services
docker-compose up -d

# Ensure services are healthy
docker-compose ps

# Monitor logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Performance Optimization

For production deployment:

1. **Use .env file for configuration:**
   ```bash
   # Create .env file in project root
   echo "REACT_APP_API_URL=https://api.example.com/api" >> .env
   ```

2. **Use resource limits** in docker-compose:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 2G
   ```

3. **Enable log rotation:**
   ```yaml
   services:
     backend:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

## Common Commands

### Container Management

```bash
# View all containers
docker-compose ps

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f

# Stop all services
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart

# Remove containers and volumes
docker-compose down
docker-compose down -v  # Also remove volumes
```

### Debugging

```bash
# Execute command in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# View container resource usage
docker stats

# Inspect network
docker network ls
docker network inspect motor-biomecanico_motor-network

# Check service health
docker-compose exec backend curl http://localhost:8000/api/health
```

### Cleanup

```bash
# Remove stopped containers
docker-compose down

# Remove all unused images
docker image prune

# Remove all unused volumes
docker volume prune

# Complete cleanup (use with caution)
docker system prune -a --volumes
```

## Environment Configuration

### Backend Environment Variables

The backend is configured via environment variables in `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1          # Unbuffered Python output
  - API_TITLE=Motor Biomecânico API
  - API_VERSION=1.0.0
  # Database (for Phase 4):
  # - DATABASE_URL=postgresql://user:password@postgres:5432/motor_biomecanico
```

### Frontend Environment Variables

The frontend uses Vite environment variables:

```yaml
environment:
  - REACT_APP_API_URL=http://backend:8000/api
  - VITE_API_URL=http://backend:8000/api
```

### Custom Configuration

Create a `.env` file in the project root:

```bash
# .env
DEBUG=false
LOG_LEVEL=info
DB_PASSWORD=secure_password_here
REACT_APP_API_URL=http://localhost:8000/api
```

Load it in docker-compose:

```yaml
services:
  backend:
    env_file:
      - .env
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Find process using port 3000
sudo lsof -i :3000

# Kill process (get PID from above)
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
# ports:
#   - "8001:8000"  # Use different external port
```

#### Services Won't Start

```bash
# Check logs for errors
docker-compose logs

# Rebuild images
docker-compose down
docker-compose build --no-cache

# Start fresh
docker-compose up
```

#### CadQuery Import Errors (Backend)

The backend might take longer to start due to CadQuery's heavy dependencies. This is normal.

```bash
# Check if backend is actually healthy
docker-compose exec backend curl http://localhost:8000/api/health

# Increase health check start period if needed
# In docker-compose.yml, adjust:
# healthcheck:
#   start_period: 60s  # Increase from 40s
```

#### Frontend Cannot Connect to Backend

```bash
# Verify services are on same network
docker network inspect motor-biomecanico_motor-network

# Check service names are correct in docker-compose.yml
# Frontend should connect to: http://backend:8000/api

# Test from frontend container
docker-compose exec frontend wget -O- http://backend:8000/api/health
```

#### Build Fails

```bash
# Clear Docker build cache
docker-compose build --no-cache

# Check Docker disk space
docker system df

# Increase Docker resources:
# macOS/Windows: Docker Desktop → Settings → Resources
# Linux: Check /var/lib/docker space
```

### Performance Tips

1. **Use named volumes for persistence:**
   ```bash
   docker volume create stl_exports
   ```

2. **Monitor resource usage:**
   ```bash
   docker stats
   ```

3. **Use `.dockerignore` files** to exclude unnecessary files from builds

4. **Layer caching:** Put frequently changing layers last in Dockerfile

5. **Use alpine base images** for smaller image sizes

### Logging and Monitoring

```bash
# View logs with timestamps
docker-compose logs --timestamps

# Filter logs
docker-compose logs backend | grep "ERROR"

# Export logs
docker-compose logs > logs.txt

# Monitor in real-time
watch -n 1 'docker-compose ps'
```

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│        Motor-Network (Docker Network)       │
│                                             │
│  ┌──────────────────┐  ┌────────────────┐  │
│  │    Frontend      │  │    Backend     │  │
│  │  (React/Vite)   │──│  (FastAPI)     │  │
│  │  Port 3000       │  │  Port 8000     │  │
│  │  (5173 dev)      │  │                │  │
│  └──────────────────┘  └────────────────┘  │
│           │                    │            │
│           └────────┬───────────┘            │
│                    │                        │
│         ┌──────────▼──────────┐            │
│         │   STL Exports Vol.  │            │
│         │ (/tmp/stl_exports)  │            │
│         └─────────────────────┘            │
│                                             │
│         [Phase 4: PostgreSQL DB]           │
│         [Will be added next]               │
└─────────────────────────────────────────────┘
```

## Next Steps

1. **Verify Services:** Run `docker-compose up` and test endpoints
2. **Database Integration:** Phase 4 will add PostgreSQL integration
3. **CI/CD Pipeline:** Set up automated builds and deployments
4. **Production Deployment:** Use Docker Registry (Docker Hub, ECR, etc.)

## Support

For issues or questions:

1. Check Docker logs: `docker-compose logs`
2. Verify network connectivity: `docker network inspect`
3. Review Dockerfile health checks
4. Consult Docker documentation: https://docs.docker.com/

---

**Motor Biomecânico Docker Setup** | Version 1.0 | 2026
