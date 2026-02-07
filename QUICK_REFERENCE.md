# Quick Deployment Reference

## 🚀 One-Command Deployment

### Local Development
```bash
python wsgi.py
```

### Docker Run
```bash
docker build -t hiring-assistant . && \
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  hiring-assistant
```

### Docker Compose
```bash
docker-compose up
```

### Heroku Deploy
```bash
git push heroku main
```

### Render Deploy
```
Connect GitHub repo → Set FLASK_ENV=production → Deploy
```

### Railway Deploy
```
Connect GitHub repo → Auto-deploy
```

## 🔐 Generate SECRET_KEY

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

Copy the output and set it in your `.env` file or platform environment variables.

## ⚙️ Environment Variables

**Minimum Required:**
```env
FLASK_ENV=production
SECRET_KEY=your-generated-secret-key
```

**Optional:**
```env
HOST=0.0.0.0
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
DEVICE=cpu
MAX_UPLOAD_SIZE=16777216
```

## 📋 Pre-Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Update `FLASK_ENV` to `production`
- [ ] Run tests locally: `python wsgi.py`
- [ ] Check `.env` not committed to git
- [ ] Verify `uploads/resumes` directory writable
- [ ] Review error.html template exists
- [ ] Check requirements.txt is complete

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `SECRET_KEY not set` | Generate and set SECRET_KEY env var |
| `Port 5000 in use` | Change PORT env var or kill process on 5000 |
| `Module not found` | Run `pip install -r requirements.txt` |
| `Memory error` | Reduce WORKERS or use CPU (DEVICE=cpu) |
| `Model download fails` | Check internet connection or set HF_HOME |
| `Upload fails` | Check uploads folder permissions |

## 🔍 Check Deployment Status

### View Logs
```bash
# Local development
tail -f app.log

# Docker
docker logs <container_id>

# Heroku
heroku logs --tail

# Railway
railway logs

# Render
View in dashboard
```

### Health Check
```bash
curl http://localhost:5000/
curl https://your-deployed-app.com/
```

## 📦 Platform-Specific Quick Setup

### Heroku
1. `heroku login`
2. `heroku create your-app-name`
3. `heroku config:set FLASK_ENV=production`
4. `heroku config:set SECRET_KEY=<generated-key>`
5. `git push heroku main`

### Railway
1. Connect GitHub and select repo
2. Add environment variables in dashboard
3. Deploy automatically

### Render
1. Create new Web Service
2. Connect GitHub
3. Set env variables: `FLASK_ENV=production`, `SECRET_KEY=<key>`
4. Deploy

### Docker Hub
```bash
docker login
docker build -t your-username/hiring-assistant .
docker push your-username/hiring-assistant
docker run -p 5000:5000 your-username/hiring-assistant
```

## 🎯 Production Tips

1. **Always use HTTPS** in production
2. **Enable CORS** if needed: `pip install flask-cors`
3. **Add rate limiting**: `pip install Flask-Limiter`
4. **Monitor logs** regularly
5. **Backup uploads** directory daily
6. **Update dependencies** monthly
7. **Use process manager** (systemd, supervisor)
8. **Configure reverse proxy** (Nginx, Apache)

## 📞 Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python wsgi.py

# Run production server (gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# Run with logging
gunicorn -w 4 -b 0.0.0.0:5000 \
  --log-level debug \
  --access-logfile access.log \
  wsgi:app

# Run with systemd
sudo systemctl start hiring-assistant
sudo systemctl status hiring-assistant
sudo journalctl -u hiring-assistant -f

# Check if running
curl http://localhost:5000/

# View logs
tail -f app.log
```

## 📊 Performance Monitoring

```bash
# CPU usage
top -p $(pgrep -f gunicorn)

# Memory usage  
ps aux | grep gunicorn

# Port usage
lsof -i :5000

# Active connections
netstat -an | grep ESTABLISHED | wc -l
```

---

**Remember:** Always test in development first, then deploy to production! 🎯
