#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def test_mortgage_app():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Enable request/response logging
        page.on("request", lambda request: print(f"REQUEST: {request.method} {request.url}"))
        page.on("response", lambda response: print(f"RESPONSE: {response.status} {response.url}"))
        
        try:
            print("Loading main page...")
            await page.goto("https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/")
            
            # Wait for page to load
            await page.wait_for_timeout(3000)
            
            print("\nTesting direct API call...")
            # Test the API call directly
            response = await page.evaluate("""
                async () => {
                    try {
                        const response = await fetch('/api/presets', {
                            method: 'GET',
                            headers: {
                                'Accept': 'application/json',
                                'Cache-Control': 'no-cache'
                            }
                        });
                        return {
                            status: response.status,
                            statusText: response.statusText,
                            headers: Object.fromEntries(response.headers.entries()),
                            body: await response.text()
                        };
                    } catch (error) {
                        return { error: error.message };
                    }
                }
            """)
            
            print(f"API Response: {response}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_mortgage_app())
