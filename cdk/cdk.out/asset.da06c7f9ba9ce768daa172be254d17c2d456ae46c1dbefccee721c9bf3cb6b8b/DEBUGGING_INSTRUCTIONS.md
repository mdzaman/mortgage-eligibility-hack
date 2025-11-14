# Debugging the Mortgage Engine UI

## Issue
The "Evaluate Scenario" button is not showing results.

## What We've Fixed

1. **Added CORS headers** to allow cross-origin requests
2. **Added comprehensive console logging** to track execution flow
3. **Added server-side logging** to see API requests

## How to Debug

### Option 1: Check Browser Console

1. Open your browser to: http://localhost:3000 (or the preview URL)
2. Open Developer Tools:
   - **Chrome/Edge**: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
   - **Firefox**: Press F12 or Ctrl+Shift+K (Cmd+Option+K on Mac)
3. Click on the "Console" tab
4. Click one of the preset buttons (e.g., "Prime Conforming")
5. Click "Evaluate Scenario"
6. Watch the console for log messages:
   - `Form submitted`
   - `Form data: {...}`
   - `Sending request to /api/evaluate...`
   - `Response status: 200`
   - `Result: {...}`
   - `Calling displayResults...`
   - `displayResults called with: {...}`
   - `Results div: <div>...</div>`
   - `Results div display set to block`
   - `Setting innerHTML with XXX characters`
   - `innerHTML set successfully`

### Option 2: Test the API Directly

Run the test script:
```bash
python3 test_api.py
```

This will test all API endpoints and confirm they're working.

### Option 3: Check Server Logs

The server now logs all requests. Check the server output for:
- `[/api/evaluate] Received POST request`
- `[/api/evaluate] Parsed request data`
- `[/api/evaluate] Running price_scenario...`
- `[/api/evaluate] Scenario evaluated successfully`
- `[/api/evaluate] Sending response...`
- `[/api/evaluate] Response sent successfully`

## Common Issues

### 1. Results Not Showing
- Check if `displayResults()` is being called (console log should show "Calling displayResults...")
- Check if there are any JavaScript errors in the console
- Check if the results div exists (console should show "Results div: <div>...")

### 2. API Errors
- Check server logs for error messages
- Look for HTTP error codes (400, 500, etc.)
- Check the error message in the alert box

### 3. CORS Errors
- Should be fixed now with CORS headers
- If you still see CORS errors, check the browser console

## Next Steps

If the issue persists after checking these:
1. Share the console log output (copy all messages from the console)
2. Share any error messages that appear
3. Check if the server is running: `curl http://localhost:3000`
