# Hiring Assistant - Deployment Guide

This is a production-ready hiring assistant application that automates resume screening and coding interviews.

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY and other configs
   ```

4. **Run development server:**
   ```bash
   python wsgi.py
   ```
   Access at `http://localhost:5000`

## Production Deployment

### Using Gunicorn (Recommended)

1. **Install production dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

3. **Run with gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   ```

### Using Docker

1. **Build image:**
   ```bash
   docker build -t hiring-assistant .
   ```

2. **Run container:**
   ```bash
   docker run -p 5000:5000 \
     -e FLASK_ENV=production \
     -e SECRET_KEY=your-secret-key \
     hiring-assistant
   ```

### Deployment on Render.com

1. Push code to GitHub
2. Connect repository to Render
3. Set environment variable: `FLASK_ENV=production`
4. Set environment variable: `SECRET_KEY=<generate-secret-key>`
5. Deploy with Build Command: `pip install -r requirements.txt`
6. Deploy with Start Command: `gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app`

### Deployment on Railway.app

1. Push code to GitHub
2. Connect repository to Railway
3. Railway auto-detects Python and installs requirements
4. Set environment variables in Railway dashboard:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<generate-secret-key>`
5. Railway auto-starts the app using Procfile

### Deployment on Heroku

1. **Create Procfile:**
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
   ```

2. **Push to Heroku:**
   ```bash
   git push heroku main
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

## Environment Variables

Key variables to configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | development | Set to 'production' for deployment |
| `SECRET_KEY` | dev-secret | **MUST change in production** |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 5000 | Server port |
| `UPLOAD_FOLDER` | uploads/resumes | Resume upload directory |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DEVICE` | cpu | Use 'cuda' for GPU acceleration |

## Important Security Checklist

- [ ] Generate and set a strong `SECRET_KEY`
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS/SSL in production
- [ ] Set appropriate `MAX_UPLOAD_SIZE`
- [ ] Configure firewall rules
- [ ] Enable CORS if needed
- [ ] Use environment variables for sensitive data
- [ ] Regular backups of uploaded resumes
- [ ] Monitor logs for errors
- [ ] Keep dependencies updated

## Monitoring & Logs

Application logs are written to `app.log` file. Monitor this for errors and performance issues.

```bash
tail -f app.log
```

## Troubleshooting

### Model Loading Issues
If the sentence-transformer model doesn't download automatically, set:
```bash
export HF_HOME=/path/to/cache
```

### Out of Memory
Reduce worker count or use CPU instead of GPU:
```bash
gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app
export DEVICE=cpu
```

### Port Already in Use
```bash
lsof -i :5000
kill -9 <PID>
```

## File Structure

```
.
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── wsgi.py               # WSGI entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── resume/               # Resume processing modules
├── project/              # Coding round modules
├── templates/            # HTML templates
└── uploads/              # User uploads (not in git)
```

## Support

For issues or questions, check the logs and ensure all environment variables are properly configured.
