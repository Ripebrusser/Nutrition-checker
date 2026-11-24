# Phase 6: Deployment Guide

**Date:** 2026-11-19  
**Status:** Ready for Deployment

---

## 1. Prerequisites

### 1.1 System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.11+ | 3.15+ |
| RAM | 2 GB | 4 GB |
| Disk | 2 GB | 5 GB |
| CPU | 2 cores | 4 cores |
| OS | Linux/Windows/macOS | Linux (production) |

### 1.2 Python Packages
```bash
pip install -r requirements.txt
```

### 1.3 External Dependencies
| Tool | Purpose |
|------|---------|
| Git | Version control |
| SQLite3 | Database (built-in) |
| Python 3.11+ | Runtime |

---

## 2. Local Development Setup

### 2.1 Clone & Setup
```bash
# Clone repository
git clone <repository-url>
cd ML_proj

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your settings
```

### 2.2 Initialize Database
```bash
# Initialize database and import recipes
python -m app.database.session
```

### 2.3 Run Application
```bash
# Development
streamlit run app/main.py

# Or with explicit python
python -m streamlit run app/main.py
```

### 2.4 Access Application
- **Local URL**: http://localhost:8501
- **Network URL**: http://<your-ip>:8501

---

## 3. Production Deployment

### 3.1 Docker Deployment (Recommended)

#### 3.1.1 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 3.1.2 docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
    environment:
      - DATABASE_URL=sqlite:///data/app.db
      - SECRET_KEY=${SECRET_KEY}
      - STREAMLIT_PORT=8501
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # Optional: Redis for session storage
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

#### 3.1.3 Deploy Commands
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop
docker-compose down

# Backup database
docker-compose exec app cp /app/data/app.db /app/backups/app_$(date +%Y%m%d).db
```

### 3.2 Manual Server Deployment (Linux)

#### 3.2.1 Systemd Service
```ini
# /etc/systemd/system/nutrition-app.service
[Unit]
Description=Indian Nutrition & Diet Planner
After=network.target

[Service]
Type=simple
User=nutrition
WorkingDirectory=/opt/nutrition-app
Environment=PATH=/opt/nutrition-app/venv/bin
EnvironmentFile=/opt/nutrition-app/.env
ExecStart=/opt/nutrition-app/venv/bin/streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3.2.2 Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name nutrition.example.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### 3.2.3 SSL (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d nutrition.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 4. Configuration

### 4.1 Environment Variables (.env)
```bash
# Application
APP_NAME=Indian Nutrition & Diet Planner
DEBUG=False

# Database
DATABASE_URL=sqlite:///data/app.db

# JWT
SECRET_KEY=your-very-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Data paths
RECIPES_PATH=data/processed/recipes.parquet
PARSED_INGREDIENTS_PATH=data/interim/phase2/parsed_recipe_ingredients.parquet
IFCT_PATH=data/interim/ifct_final_candidate/ifct_table1_candidate.parquet

# Streamlit
STREAMLIT_PORT=8501
STREAMLIT_ADDRESS=0.0.0.0

# Security
BCRYPT_ROUNDS=12
```

### 4.2 Generate Secure Secret
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 5. Database Management

### 5.1 Initialization
```bash
# Initialize tables
python -m app.database.session

# Import recipes (one-time)
python -c "from app.database.session import init_recipe_data; init_recipe_data()"
```

### 5.2 Migrations (Alembic)
```bash
# Initialize alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Check current revision
alembic current

# Downgrade
alembic downgrade -1
```

### 5.3 Backup & Restore
```bash
# Backup
sqlite3 data/app.db .dump > backup_$(date +%Y%m%d).sql

# Restore
sqlite3 data/app.db < backup_20261119.sql
```

---

## 5. Data Management

### 5.1 Frozen Datasets (Read-Only)
| File | Purpose | Update Process |
|------|---------|----------------|
| recipes.parquet | 6,865 recipes | Manual replacement |
| parsed_recipe_ingredients.parquet | 90,862 ingredients | Phase 2 pipeline |
| ifct_table1_candidate.parquet | 528 IFCT foods | Phase 3 pipeline |
| ifct_match_candidates.parquet | 119,474 matches | Phase 3 pipeline |
| approved_mappings.jsonl | Approved mappings | Review app (Phase 3.4) |

### 5.2 Data Integrity
```bash
# Verify hashes
python -c "
import hashlib
files = [
    'data/processed/recipes.parquet',
    'data/interim/phase2/parsed_recipe_ingredients.parquet',
    'data/interim/ifct_final_candidate/ifct_table1_candidate.parquet',
]
expected = {
    'data/processed/recipes.parquet': '08710983213938c3fecafd20991ab7d3d7fe51b179303bbe4dc93b2ac1b1b6e5',
    # ... other hashes
}
for f in files:
    h = hashlib.sha256(open(f,'rb').read()).hexdigest()
    assert h == expected[f], f'{f}: {h} != {expected[f]}'
    print(f'OK: {f}')
"
```

---

## 6. Security Checklist

### 6.1 Pre-Deployment
- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set DEBUG=False
- [ ] Configure secure cookies (HttpOnly, Secure, SameSite)
- [ ] Set up firewall (allow only 80/443)
- [ ] Disable debug mode
- [ ] Remove test accounts
- [ ] Set up log rotation

### 6.2 Ongoing Security
- [ ] Regular dependency updates (`pip-audit`)
- [ ] Monitor failed login attempts
- [ ] Log audit trail for sensitive actions
- [ ] Backup encryption at rest
- [ ] Regular security scanning

---

## 7. Monitoring & Logging

### 7.1 Application Logs
```python
# app/utils/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 7.2 Key Metrics to Monitor
| Metric | Alert Threshold |
|--------|-----------------|
| Response time > 5s | Warning |
| Error rate > 1% | Critical |
| Memory > 80% | Warning |
| Disk > 80% | Warning |
| Failed logins > 10/min | Critical |

### 7.3 Log Rotation
```bash
# /etc/logrotate.d/nutrition-app
/opt/nutrition-app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 7. Backup Strategy

| Data | Frequency | Retention |
|------|-----------|-----------|
| SQLite DB | Daily | 30 days |
| Frozen datasets | Never (immutable) | Permanent |
| Logs | Daily | 30 days |
| Config | On change | 90 days |

---

## 8. Troubleshooting

### 8.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Database locked" | Concurrent access | Use connection pooling |
| "Module not found" | Missing deps | `pip install -r requirements.txt` |
| "Port 8501 in use" | Port conflict | Change port or kill process |
| "Permission denied" | File permissions | `chmod 644 data/app.db` |
| "Secret key error" | Missing .env | Copy .env.example to .env |

### 8.2 Debug Commands
```bash
# Check database
sqlite3 data/app.db ".tables"
sqlite3 data/app.db "SELECT * FROM users;"

# Check logs
tail -f logs/app.log

# Test database connection
python -c "from app.database.session import get_db; db = next(get_db()); print(db.execute('SELECT 1').scalar())"

# Clear cache
streamlit cache clear
```

---

## 9. Rollback Procedure

```bash
# 1. Stop service
sudo systemctl stop nutrition-app

# 2. Restore database
cp backups/app_20261118.db data/app.db

# 3. Restore code (if needed)
git checkout v1.2.3

# 4. Restart
sudo systemctl start nutrition-app

# 5. Verify
curl http://localhost:8501/_stcore/health
```

---

*End of Deployment Guide*