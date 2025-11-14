#!/usr/bin/env python3
"""Test script to reproduce the 403 error"""
import urllib.request
import urllib.error
import json

API_URL = "https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/"

def test_endpoint(url, method='GET', headers=None):
    """Test an endpoint with specific method and headers"""
    if headers is None:
        headers = {}

    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    print(f"Headers: {headers}")
    print(f"{'='*60}")

    try:
        req = urllib.request.Request(url, method=method, headers=headers)
        with urllib.request.urlopen(req) as response:
            status = response.status
            response_headers = dict(response.headers)
            body = response.read().decode('utf-8')

            print(f"✅ Status: {status}")
            print(f"Response Headers: {json.dumps(response_headers, indent=2)}")
            if len(body) < 200:
                print(f"Body: {body}")
            else:
                print(f"Body: {body[:200]}...")
            return True

    except urllib.error.HTTPError as e:
        print(f"❌ HTTPError: {e.code} {e.reason}")
        print(f"Response Headers: {dict(e.headers)}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Error Body: {error_body}")
        except:
            pass
        return False
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 TESTING MORTGAGE ELIGIBILITY API FOR 403 ERRORS")
    print(f"API Base URL: {API_URL}\n")

    # Test 1: GET root (should work)
    test_endpoint(API_URL, 'GET')

    # Test 2: HEAD root (likely to fail with 403)
    test_endpoint(API_URL, 'HEAD')

    # Test 3: GET /api/presets (should work)
    test_endpoint(f"{API_URL}api/presets", 'GET')

    # Test 4: HEAD /api/presets (likely to fail with 403)
    test_endpoint(f"{API_URL}api/presets", 'HEAD')

    # Test 5: OPTIONS /api/presets (should work due to CORS)
    test_endpoint(f"{API_URL}api/presets", 'OPTIONS')

    # Test 6: GET with browser-like headers
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    test_endpoint(API_URL, 'GET', browser_headers)

    # Test 7: PUT method (should fail - not configured)
    test_endpoint(API_URL, 'PUT')

    # Test 8: DELETE method (should fail - not configured)
    test_endpoint(API_URL, 'DELETE')

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
