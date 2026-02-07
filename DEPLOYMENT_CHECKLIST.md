# Production Deployment Checklist

## Pre-Deployment Configuration

### 1. Environment Setup
- [ ] Generate strong `SECRET_KEY`:
  ```bash
  python -c 'import secrets; print(secrets.token_hex(32))'
  ```
- [ ] Create `.env` file from `.env.example`
- [ ] Set `FLASK_ENV=production`
- [ ] Update all required environment variables
- [ ] Verify `UPLOAD_FOLDER` path is writable

### 2. Dependency Management
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify all packages installed correctly
- [ ] Check Python version (3.8+)
- [ ] Test imports: `python -c "from app import app; print('OK')"`

### 3. Security Checks
- [ ] SECRET_KEY is not in version control (only in `.env`)
- [ ] `.gitignore` properly configured
- [ ] No hardcoded credentials in code
- [ ] HTTPS/SSL certificate ready
- [ ] CORS configuration reviewed
- [ ] File upload restrictions in place

### 4. Application Testing
- [ ] Run `python wsgi.py` in development mode
- [ ] Test main routes (/, /admin, /applicant, etc.)
- [ ] Test file upload functionality
- [ ] Verify logging works (`app.log` created)
- [ ] Test error handlers (404, 500)
- [ ] Test with sample resume files (PDF, DOCX)

### 5. Model & Data
- [ ] Sentence Transformer model downloads on first request
- [ ] Verify model can load without internet (if cached)
- [ ] Test resume parsing with sample files
- [ ] Verify scoring works correctly

### 6. Deployment Method Selection

#### Option A: Docker
- [ ] `docker build -t hiring-assistant .` succeeds
- [ ] `docker run -p 5000:5000 -e SECRET_KEY=xxx hiring-assistant` works
- [ ] Container logs show no errors
- [ ] Upload directory persists with volumes

#### Option B: Gunicorn (Linux/Mac)
- [ ] Install gunicorn: `pip install gunicorn`
- [ ] Test: `gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app`
- [ ] Verify workers are running
- [ ] Monitor resource usage

#### Option C: Cloud Platforms

**Render.com:**
- [ ] Repository connected
- [ ] Environment variables set in dashboard
- [ ] Deploy button successful
- [ ] Logs show startup messages

**Railway.app:**
- [ ] Repository connected
- [ ] Environment variables configured
- [ ] Auto-deploys from git
- [ ] Health check passing

**Heroku:**
- [ ] Procfile created and committed
- [ ] runtime.txt specifies Python version
- [ ] `git push heroku main` succeeds
- [ ] `heroku logs --tail` shows app running

### 7. Post-Deployment Validation

- [ ] Application accessible at deployment URL
- [ ] All routes working (/dashboard, /applicant, etc.)
- [ ] File uploads working
- [ ] Resume scoring functional
- [ ] Logs accessible (`app.log` or platform logs)
- [ ] Error pages display correctly
- [ ] Static files loading (CSS, JS)
- [ ] Database migrations applied (if any)

### 8. Monitoring & Logging

- [ ] Log aggregation configured (if needed)
- [ ] Error alerts set up
- [ ] Performance monitoring in place
- [ ] Regular log rotation configured
- [ ] Backup strategy defined
- [ ] Disk space monitoring active

### 9. Performance Optimization

- [ ] Gunicorn workers optimized for server CPU count
- [ ] Model caching working correctly
- [ ] Request timeouts configured
- [ ] File upload size limits enforced
- [ ] Database queries optimized (if using DB)

### 10. Rollback Plan

- [ ] Previous version tagged in git
- [ ] Rollback procedure documented
- [ ] Database backup taken
- [ ] Traffic switch tested

## Quick Deployment Commands

### Docker Deployment
```bash
# Build
docker build -t hiring-assistant .

# Run locally
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  -v uploads:/app/uploads \
  hiring-assistant
```

### Gunicorn Deployment (Linux)
```bash
# Install
pip install gunicorn

# Run
FLASK_ENV=production SECRET_KEY=your-secret-key \
  gunicorn -w 4 \
  -b 0.0.0.0:5000 \
  --log-level info \
  --access-logfile /var/log/hiring/access.log \
  --error-logfile /var/log/hiring/error.log \
  wsgi:app
```

### Systemd Service (Linux)
Create `/etc/systemd/system/hiring-assistant.service`:
```ini
[Unit]
Description=Hiring Assistant
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/app
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hiring-assistant
sudo systemctl start hiring-assistant
```

## Environment Variables Reference

```bash
# Essential
FLASK_ENV=production
SECRET_KEY=<generated-secret>

# Server
HOST=0.0.0.0
PORT=5000
WORKERS=4

# Storage
UPLOAD_FOLDER=/var/data/uploads/resumes
MAX_UPLOAD_SIZE=16777216

# Model
MODEL_NAME=all-MiniLM-L6-v2
DEVICE=cpu

# Logging
LOG_LEVEL=INFO
```

## Troubleshooting Common Issues

### Model Won't Load
```bash
# Set HuggingFace cache
export HF_HOME=/path/to/cache
python wsgi.py
```

### Port Already in Use
```bash
lsof -i :5000
kill -9 <PID>
```

### Memory Issues
```bash
# Reduce workers
gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app

# Use CPU instead of GPU
export DEVICE=cpu
```

### File Upload Fails
- Check upload folder permissions
- Verify MAX_UPLOAD_SIZE setting
- Check disk space availability

## Support & Maintenance

- Monitor `app.log` for errors
- Check system resources regularly
- Update dependencies monthly
- Backup uploaded resumes daily
- Test disaster recovery quarterly
