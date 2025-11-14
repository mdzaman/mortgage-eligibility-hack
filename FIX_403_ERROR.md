# Fix for HTTP 403 Error

## Problem

Users were experiencing HTTP 403 errors when accessing the mortgage eligibility application from browsers and mobile phones. The error message was:

```
HTTP/2 403 Forbidden
x-amzn-ErrorType: MissingAuthenticationTokenException
```

## Root Cause

The issue was that the API Gateway was not configured to handle **HEAD requests**. When browsers or HTTP clients send HEAD requests (which is common for:
- Checking resource availability
- Caching validation
- Preflight checks
- Security scanning tools

...API Gateway would return a 403 error with the misleading message "MissingAuthenticationTokenException" because it couldn't find a matching route for the HEAD method.

## Testing

The issue was reproduced using the test script `test_403_error.py` which showed:

- ✅ GET requests to all endpoints: **Working** (200 OK)
- ✅ OPTIONS requests: **Working** (204 No Content)
- ❌ HEAD requests to all endpoints: **Failing** (403 Forbidden)

## Solution

The fix involved three changes:

### 1. CDK Stack (cdk/mortgage_stack.py)

Added HEAD method support to all API Gateway resources:

```python
# Root endpoint
api.root.add_method("HEAD", lambda_integration, ...)

# /evaluate endpoints
evaluate.add_method("HEAD", lambda_integration)
api_evaluate.add_method("HEAD", lambda_integration)

# /presets endpoints
presets.add_method("HEAD", lambda_integration)
api_presets.add_method("HEAD", lambda_integration)
```

### 2. Lambda Handler (genai-mortgage-hack/lambda_handler.py)

Added explicit HEAD request handling:

```python
# Updated CORS headers to include HEAD
cors_headers = {
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,HEAD',
    ...
}

# Added HEAD handlers for each endpoint
if path == '/' and method == 'HEAD':
    return {
        'statusCode': 200,
        'headers': {**cors_headers, 'Content-Type': 'text/html'},
        'body': ''  # Empty body for HEAD requests
    }
```

### 3. Local Server (genai-mortgage-hack/server.py)

Added `do_HEAD()` method to handle HEAD requests for local testing:

```python
def do_HEAD(self):
    """Handle HEAD requests (fixes 403 errors)"""
    # Returns appropriate headers with no body
```

## Verification

After implementing the fix, all tests pass:

```bash
$ python3 test_lambda_head_fix.py
TEST RESULTS: 6 passed, 0 failed
```

The Lambda handler now correctly:
- Returns 200 OK for HEAD requests
- Includes proper CORS headers
- Returns empty body (as per HTTP HEAD specification)
- Works for all endpoints: `/`, `/api/presets`, `/presets`, `/api/evaluate`, `/evaluate`

## Deployment

To deploy the fix:

1. Navigate to the CDK directory:
   ```bash
   cd cdk
   ```

2. Deploy the updated stack:
   ```bash
   cdk deploy
   ```

3. The changes will automatically update the Lambda function and API Gateway configuration

## Expected Outcome

After deployment:
- ✅ HEAD requests will return 200 OK
- ✅ Browsers will no longer receive 403 errors
- ✅ Mobile phones will be able to access the application
- ✅ All existing functionality (GET, POST, OPTIONS) continues to work

## Additional Notes

- The "MissingAuthenticationTokenException" error is misleading - it doesn't actually mean authentication is required. It's API Gateway's default error when no route matches the HTTP method.
- HEAD requests are important for HTTP compliance and are commonly used by browsers, CDNs, and load balancers.
- The fix maintains backward compatibility - all existing functionality continues to work as before.
