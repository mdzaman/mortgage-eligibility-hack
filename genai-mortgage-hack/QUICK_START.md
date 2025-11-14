# Quick Start Guide

## Fixed Issues ✅

1. **CSRF Error**: Disabled CSRF protection in Flask app
2. **Port Conflict**: Changed default ports:
   - Flask app: Port **8080** (was 3000)
   - Simple HTTP server: Port **8081** (was 3000)
3. **CORS Headers**: Added proper CORS headers to all API endpoints

## How to Run

### Option 1: Using the launcher script (Easiest)
```bash
cd genai-mortgage-hack
./run.sh
```
Then select option 1 for Flask or option 2 for Simple HTTP server.

### Option 2: Run Flask app directly
```bash
cd genai-mortgage-hack
python3 app.py
```
Access at: http://localhost:8080

### Option 3: Run Simple HTTP server
```bash
cd genai-mortgage-hack
python3 server.py
```
Access at: http://localhost:8081

### Option 4: Custom port
```bash
# Flask app on custom port
PORT=5000 python3 app.py

# Simple HTTP server on custom port
PORT=5000 python3 server.py
```

## What Was Fixed

### app.py Changes:
- Added `app.config['WTF_CSRF_ENABLED'] = False` to disable CSRF
- Added CORS headers to all API responses
- Added OPTIONS method handlers for preflight requests
- Changed default port from 3000 to 8080
- Added PORT environment variable support

### server.py Changes:
- Changed default port from 3000 to 8081
- Added PORT environment variable support

## Troubleshooting

If you still get errors:

1. **Port already in use**: 
   - Check what's running: `lsof -i :8080`
   - Kill the process: `kill -9 <PID>`
   - Or use a different port: `PORT=9000 python3 app.py`

2. **Module not found**:
   - Make sure you're in the correct directory
   - Install dependencies if needed

3. **CSRF still appearing**:
   - Clear your browser cache
   - Try incognito/private mode
   - Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
