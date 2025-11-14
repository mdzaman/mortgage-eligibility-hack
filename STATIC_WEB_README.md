# Static Web Hosting Setup

## Architecture Overview

The mortgage eligibility application now uses a **static web hosting** architecture to eliminate 403 errors:

### Components:
1. **Static Web UI**: HTML/CSS/JavaScript hosted on S3 + CloudFront
2. **API Backend**: Lambda functions behind API Gateway (unchanged)

### URLs:
- **Web Application**: https://d3eli7luy051tr.cloudfront.net
- **S3 Direct**: http://mortgage-eligibility-web-227462955655-us-east-1.s3-website-us-east-1.amazonaws.com
- **API Endpoint**: https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/

## Benefits:
✅ **No more 403 errors** - Static files served directly from S3/CloudFront  
✅ **Better performance** - CDN distribution via CloudFront  
✅ **Separation of concerns** - UI and API are decoupled  
✅ **Scalability** - Static assets scale automatically  

## File Structure:
```
static-web/
├── index.html      # Main web interface
├── styles.css      # CSS styling
├── app.js          # JavaScript application logic
└── config.js       # API endpoint configuration
```

## Configuration:
To update the API endpoint, modify `static-web/config.js`:
```javascript
window.API_CONFIG = {
    BASE_URL: 'https://your-api-gateway-url.com/prod'
};
```

## Deployment:
Run the deployment script to update both static files and API:
```bash
./deploy.sh
```

## API Endpoints:
- `POST /api/evaluate` - Mortgage eligibility evaluation
- `GET /api/presets` - Load preset scenarios

The static web application makes CORS-enabled requests to these API endpoints.
