# Deployment Guide

## Local Development

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd retailpulse

# Run startup script
./start.sh
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

Access at: `http://localhost:5001`

## Production Deployment

### Option 1: Traditional Server (Ubuntu/Debian)

#### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx
```

#### 2. Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/retailpulse
cd /var/www/retailpulse

# Clone repository
git clone <repository-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Create Systemd Service

Create `/etc/systemd/system/retailpulse.service`:

```ini
[Unit]
Description=RetailPulse Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/retailpulse
Environment="PATH=/var/www/retailpulse/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/var/www/retailpulse/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 run:app

[Install]
WantedBy=multi-user.target
```

#### 4. Configure Nginx

Create `/etc/nginx/sites-available/retailpulse`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/retailpulse/app/static;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/retailpulse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Start Service

```bash
sudo systemctl start retailpulse
sudo systemctl enable retailpulse
sudo systemctl status retailpulse
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application
COPY . .

# Expose port
EXPOSE 5001

# Set environment
ENV FLASK_ENV=production

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "run:app"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

#### 3. Build and Run

```bash
docker-compose up -d
```

### Option 3: Cloud Platforms

#### Heroku

1. Create `Procfile`:
```
web: gunicorn run:app
```

2. Deploy:
```bash
heroku create retailpulse
git push heroku main
```

#### AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize and deploy:
```bash
eb init -p python-3.11 retailpulse
eb create retailpulse-env
eb deploy
```

#### Google Cloud Run

1. Create `Dockerfile` (see Docker section)

2. Deploy:
```bash
gcloud run deploy retailpulse \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

Create `.env` file:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATA_PATH=/path/to/data/cleandataset.csv
```

## Performance Tuning

### Gunicorn Workers

Calculate optimal workers:
```
workers = (2 × CPU_cores) + 1
```

Example for 4 cores:
```bash
gunicorn -w 9 -b 0.0.0.0:5001 run:app
```

### Nginx Caching

Add to nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_pass http://127.0.0.1:5001;
}
```

## Monitoring

### Application Logs

```bash
# Systemd service logs
sudo journalctl -u retailpulse -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Check Endpoint

Add to `app/routes/main.py`:
```python
@main_bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200
```

## Backup Strategy

### Data Backup

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Upload to S3 (example)
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

### Automated Backups

Create cron job:
```bash
0 2 * * * /path/to/backup-script.sh
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure firewall (UFW/iptables)
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Restrict file permissions
- [ ] Use environment variables for secrets
- [ ] Enable CORS properly
- [ ] Implement rate limiting
- [ ] Regular backups

## Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u retailpulse -n 50

# Check Python path
which python
python --version

# Verify dependencies
pip list
```

### High memory usage

```bash
# Monitor memory
htop

# Reduce Gunicorn workers
# Edit systemd service file
```

### Slow response times

```bash
# Check application logs
# Enable query profiling
# Add caching layer
# Optimize database queries
```

## Maintenance

### Update Application

```bash
cd /var/www/retailpulse
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart retailpulse
```

### Database Maintenance

```bash
# Backup before maintenance
# Run data cleanup scripts
# Optimize indexes
```

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Email: support@retailpulse.com
- Documentation: <docs-url>
