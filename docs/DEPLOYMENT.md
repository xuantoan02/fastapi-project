# Deployment Guide

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=false`
- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure production `DATABASE_URL`
- [ ] Set appropriate `CORS_ORIGINS`
- [ ] Enable SSL/TLS
- [ ] Configure reverse proxy (nginx/traefik)
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Set up database backups

## Generating Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Docker Deployment

### Build Image

```bash
docker build -t fastapi-project:v1.0.0 .
```

### Run Container

```bash
docker run -d \
  --name fastapi-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-secret \
  -e DEBUG=false \
  fastapi-project:v1.0.0
```

### Docker Compose Production

Create `docker-compose.prod.yml`:

```yaml
version: "3.9"

services:
  api:
    image: fastapi-project:latest
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEBUG=false
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Cloud Deployment

### AWS ECS

1. Push image to ECR
2. Create ECS task definition
3. Configure Application Load Balancer
4. Set up ECS service

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/fastapi-project

# Deploy
gcloud run deploy fastapi-project \
  --image gcr.io/PROJECT_ID/fastapi-project \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-project
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-project
  template:
    metadata:
      labels:
        app: fastapi-project
    spec:
      containers:
      - name: api
        image: fastapi-project:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /api/v1/health/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
```

## Nginx Reverse Proxy

```nginx
upstream fastapi {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Database Migrations in Production

```bash
# Always backup before migrations
pg_dump -h host -U user dbname > backup.sql

# Run migrations
./scripts/migrate.sh upgrade
```

## Monitoring

### Health Endpoints

- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/ready` - Readiness check

### Recommended Tools

- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack or Loki
- **APM**: Datadog, New Relic, or Sentry
- **Uptime**: Pingdom or UptimeRobot
