const https = require('https');

function makeRequest(url, headers = {}) {
    return new Promise((resolve, reject) => {
        const options = {
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                ...headers
            }
        };

        const req = https.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                resolve({
                    status: res.statusCode,
                    headers: res.headers,
                    body: data
                });
            });
        });

        req.on('error', reject);
        req.end();
    });
}

async function test() {
    console.log('Testing main page...');
    try {
        const mainPage = await makeRequest('https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/');
        console.log(`Main page: ${mainPage.status}`);
        
        console.log('\nTesting /api/presets with browser headers...');
        const apiTest = await makeRequest('https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/api/presets', {
            'Origin': 'https://gm515kqhwd.execute-api.us-east-1.amazonaws.com',
            'Referer': 'https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/'
        });
        
        console.log(`API presets: ${apiTest.status}`);
        console.log('Response headers:', apiTest.headers);
        
        if (apiTest.status !== 200) {
            console.log('Response body:', apiTest.body);
        } else {
            console.log('SUCCESS: API working');
        }
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

test();
