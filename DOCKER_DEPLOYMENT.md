# Docker Deployment Guide

## Overview
This guide covers containerizing and deploying the Products API using Docker and Docker Compose.

## Prerequisites

### Required Software
- **Docker**: Version 20.10 or higher
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS/Windows)
  - Or Docker Engine for Linux
- **Docker Compose**: Version 2.0 or higher (included with Docker Desktop)

### Verify Installation
```bash
docker --version
docker-compose --version
```

## Docker Files

### 1. Dockerfile
**Location:** `Dockerfile`

**Features:**
- Multi-stage build for smaller image size
- Python 3.13 slim base image
- Non-root user for security
- Health check included
- Production-ready configuration

**Image Size:** ~150-200 MB (compared to ~1GB with full Python image)

### 2. docker-compose.yml
**Location:** `docker-compose.yml`

**Services:**
- **mongodb**: MongoDB 7.0 database with persistent storage
- **app**: Flask application

**Features:**
- Service dependency management
- Health checks for both services
- Persistent volumes for data
- Network isolation
- Environment variable configuration

### 3. .dockerignore
**Location:** `.dockerignore`

**Purpose:** Exclude unnecessary files from Docker build context
- Reduces build time
- Decreases image size
- Improves security (no test files, secrets, etc.)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

#### Start All Services
```bash
# Build and start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app
docker-compose logs -f mongodb
```

#### Stop Services
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (deletes data!)
docker-compose down -v
```

#### Check Service Status
```bash
# List running containers
docker-compose ps

# Check service health
docker-compose exec app python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5002/health').read())"
```

### Option 2: Using Docker Commands Directly

#### Build Image
```bash
docker build -t products-api:latest .
```

#### Run MongoDB Container
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  -v mongodb_data:/data/db \
  mongo:7.0
```

#### Run Application Container
```bash
docker run -d \
  --name products-api \
  -p 5002:5002 \
  -e MONGO_URI="mongodb://admin:admin123@host.docker.internal:27017/products?authSource=admin" \
  products-api:latest
```

## Access the Application

Once containers are running:

- **Web UI**: http://localhost:5002
- **API**: http://localhost:5002/api/products
- **Health Check**: http://localhost:5002/health
- **MongoDB**: localhost:27017

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | See docker-compose.yml | MongoDB connection string |
| `DATABASE_NAME` | `products` | Database name |
| `COLLECTION_NAME` | `fruits` | Collection name |
| `FLASK_ENV` | `production` | Flask environment |

### Customize Configuration

Edit `docker-compose.yml` to change environment variables:

```yaml
app:
  environment:
    MONGO_URI: "your-connection-string"
    DATABASE_NAME: "your-database"
    COLLECTION_NAME: "your-collection"
```

## Development Mode

### Enable Code Hot-Reload

Uncomment volume mounts in `docker-compose.yml`:

```yaml
app:
  volumes:
    - ./products.py:/app/products.py
    - ./templates:/app/templates
    - ./static:/app/static
```

This allows code changes to reflect immediately without rebuilding the image.

### Rebuild After Code Changes

```bash
# Rebuild and restart services
docker-compose up -d --build

# Or rebuild specific service
docker-compose build app
docker-compose up -d app
```

## Docker Commands Reference

### Container Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove containers
docker-compose down

# View running containers
docker-compose ps

# View container logs
docker-compose logs -f [service_name]
```

### Image Management

```bash
# Build image
docker-compose build

# Pull latest images
docker-compose pull

# Remove unused images
docker image prune -a

# List images
docker images
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect products_mongodb_data

# Remove all volumes (WARNING: deletes data!)
docker-compose down -v

# Backup volume
docker run --rm -v products_mongodb_data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb-backup.tar.gz /data
```

### Debugging

```bash
# Execute command in running container
docker-compose exec app bash
docker-compose exec mongodb mongosh

# View container details
docker inspect products-api

# Check resource usage
docker stats

# View container processes
docker-compose top
```

## Health Checks

### Application Health Check
```bash
curl http://localhost:5002/health
```

Expected response:
```json
{
  "message": "Products API is running",
  "status": "healthy",
  "database": "connected",
  "endpoints": {...}
}
```

### MongoDB Health Check
```bash
docker-compose exec mongodb mongosh --eval "db.runCommand({ping: 1})"
```

### Docker Health Status
```bash
docker inspect --format='{{.State.Health.Status}}' products-api
docker inspect --format='{{.State.Health.Status}}' products-mongodb
```

## Production Deployment

### Best Practices

1. **Use Environment Variables**
   - Never hardcode credentials in Dockerfile or docker-compose.yml
   - Use `.env` file or Docker secrets

2. **Enable Resource Limits**
   ```yaml
   app:
     deploy:
       resources:
         limits:
           cpus: '1.0'
           memory: 512M
         reservations:
           cpus: '0.5'
           memory: 256M
   ```

3. **Use Docker Secrets** (for Docker Swarm)
   ```yaml
   secrets:
     db_password:
       external: true
   ```

4. **Enable Logging**
   ```yaml
   app:
     logging:
       driver: "json-file"
       options:
         max-size: "10m"
         max-file: "3"
   ```

5. **Use Production MongoDB**
   - Replace local MongoDB with cloud service (MongoDB Atlas)
   - Update MONGO_URI in environment variables

### Security Considerations

1. **Non-Root User**: Application runs as `appuser` (not root)
2. **Minimal Base Image**: Uses Python slim image
3. **No Secrets in Image**: Environment variables only
4. **Network Isolation**: Services on dedicated network
5. **Health Checks**: Automatic restart on failure

### Sample .env File

Create `.env` file in project root:

```env
# MongoDB Configuration
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=secure_password_here
MONGO_DATABASE=products
MONGO_COLLECTION=fruits

# Flask Configuration
FLASK_ENV=production
```

Update docker-compose.yml to use .env:

```yaml
mongodb:
  environment:
    MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER}
    MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
```

## Backup and Restore

### Backup MongoDB Data

```bash
# Create backup directory
mkdir -p backups

# Backup using mongodump
docker-compose exec mongodb mongodump \
  --out=/data/backup \
  --username=admin \
  --password=admin123 \
  --authenticationDatabase=admin

# Copy backup from container
docker cp products-mongodb:/data/backup ./backups/
```

### Restore MongoDB Data

```bash
# Copy backup to container
docker cp ./backups/backup products-mongodb:/data/

# Restore using mongorestore
docker-compose exec mongodb mongorestore \
  /data/backup \
  --username=admin \
  --password=admin123 \
  --authenticationDatabase=admin
```

## Troubleshooting

### Container Won't Start

```bash
# Check container logs
docker-compose logs app

# Check if port is already in use
lsof -i :5002
```

### Cannot Connect to MongoDB

```bash
# Check if MongoDB is running
docker-compose ps mongodb

# Check MongoDB logs
docker-compose logs mongodb

# Verify connection string
docker-compose exec app env | grep MONGO_URI
```

### Permission Errors

```bash
# Check file permissions
ls -la

# Ensure volumes are writable
docker-compose exec app ls -la /app
```

### Image Build Failures

```bash
# Clean build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Health Check Failures

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' products-api

# Test health endpoint manually
docker-compose exec app curl http://localhost:5002/health
```

## Monitoring

### View Resource Usage

```bash
# All containers
docker stats

# Specific container
docker stats products-api
```

### View Container Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Since specific time
docker-compose logs --since=1h
```

## CI/CD Integration

### GitHub Actions Example

Add to `.github/workflows/docker.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t products-api:${{ github.sha }} .
      
      - name: Run tests in container
        run: |
          docker run --rm products-api:${{ github.sha }} \
            python -m pytest tests/
```

## Performance Optimization

### Image Size Optimization

- **Multi-stage build**: Reduces final image size by ~70%
- **Slim base image**: 150MB vs 1GB for full Python image
- **.dockerignore**: Excludes 50+ MB of unnecessary files

### Runtime Optimization

- **Health checks**: Automatic restart on failure
- **Resource limits**: Prevents resource exhaustion
- **Persistent volumes**: Fast database access

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)
- [Python Docker Image](https://hub.docker.com/_/python)

## Support

For issues related to:
- **Docker setup**: Check this documentation
- **Application code**: See main README.md
- **Tests**: See tests/README.md
- **CI/CD**: See CI_CD_IMPLEMENTATION.md

## Summary

✅ **Multi-stage Dockerfile** for optimized image size
✅ **Docker Compose** for easy orchestration
✅ **Health checks** for both services
✅ **Persistent volumes** for data durability
✅ **Security** with non-root user
✅ **Production-ready** configuration
✅ **Development mode** support with hot-reload

The containerized application is ready for deployment to any Docker-compatible environment!
