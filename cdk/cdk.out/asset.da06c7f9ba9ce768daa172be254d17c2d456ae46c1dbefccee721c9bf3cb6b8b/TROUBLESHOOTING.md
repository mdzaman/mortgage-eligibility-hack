# Troubleshooting CSRF and JSON Errors

## Issues Reported
1. **Preset Loading Error:** "Error: Unexpected token '<', '<!doctype …' is not valid JSON"
2. **Evaluate Error:** "Error: Server error 400: Something is wrong with your CSRF token"

## Analysis

These errors suggest that the **preview proxy** (Coder's reverse proxy service) is intercepting requests and either:
- Adding CSRF protection
- Redirecting to an error page
- Modifying the responses

The local server (localhost:3000) is working correctly when tested directly via curl, but the preview URL is experiencing issues.

## Actions Taken

### 1. Enhanced Error Handling
Updated both `/templates/index.html` with better error handling:

**For Preset Loading:**
```javascript
- Added detailed logging of response status, content-type, and body
- Check if response is HTML instead of JSON
- Log first 200 characters of response for debugging
```

**For Evaluate Endpoint:**
```javascript
- Added Accept, Cache-Control headers
- Added credentials: 'same-origin'
- Enhanced error messages to capture actual response content
```

### 2. Created Diagnostic Tool

A comprehensive diagnostic page is now available at:
**https://preview--dev--mortgage-agent-developer--mohammad-m-zaman./diagnostic**

This tool will:
- Test all API endpoints
- Show response status codes, headers, and bodies
- Identify if responses are JSON or HTML
- Detect CSRF token errors
- Display page and connection information

## How to Use the Diagnostic Tool

1. **Open the diagnostic page:**
   - Go to: https://preview--dev--mortgage-agent-developer--mohammad-m-zaman./diagnostic

2. **Click "Run All Tests"** - This will test:
   - Homepage (GET /)
   - Presets API (GET /api/presets)
   - Evaluate API (POST /api/evaluate)

3. **Review the results:**
   - Green text = success
   - Red text = errors
   - Look for:
     - Response status codes (should be 200)
     - Content-Type headers (should be application/json for APIs)
     - Whether responses are HTML or JSON
     - Any CSRF token messages

4. **Copy the diagnostic output** and share it so we can:
   - Identify exactly what the proxy is returning
   - See if requests are being modified
   - Determine the root cause

## Additional Test Pages

All test pages are available:
- `/` - Main application UI
- `/diagnostic` - Diagnostic tool (NEW)
- `/simple-test` - Simple API test
- `/test` - Full API test suite
- `/test-presets` - Preset loading test

## Server Status

The server is running correctly on port 3000:
```bash
✓ GET /              → 200 OK (HTML)
✓ GET /api/presets   → 200 OK (JSON, 1600+ bytes)
✓ POST /api/evaluate → 200 OK (JSON, 2335 bytes)
```

## What to Check

When you run the diagnostic tool, look for:

1. **If response is HTML instead of JSON:**
   - The proxy might be returning an error page
   - Check the HTML content for error messages

2. **If you see CSRF errors:**
   - The proxy is adding CSRF protection
   - We may need to adjust how we're making requests

3. **If content-type is wrong:**
   - Should be `application/json` for API endpoints
   - If it's `text/html`, the proxy is redirecting

4. **If the URL changes:**
   - The diagnostic tool shows the final URL after redirects
   - This will tell us if requests are being redirected elsewhere

## Next Steps

Please:
1. Open the diagnostic tool
2. Click "Run All Tests"
3. Take a screenshot or copy the output
4. Share the results

This will help us identify exactly what's happening with the preview proxy and how to fix it.

## Alternative: Direct Access

If the preview URL continues to have issues, you could also:
- Access the Coder workspace terminal
- Run: `curl http://localhost:3000` to verify local server works
- Consider if there's a way to access the workspace's port 3000 directly

The server itself is functioning perfectly - these errors are related to how the preview proxy is handling requests.
