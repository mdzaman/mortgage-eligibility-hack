#!/usr/bin/env python3
"""Test the Lambda handler with HEAD request support"""
import sys
import os

# Add the genai-mortgage-hack directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'genai-mortgage-hack'))

from lambda_handler import handler

def test_head_requests():
    """Test that HEAD requests work properly"""

    print("="*60)
    print("TESTING LAMBDA HANDLER WITH HEAD REQUESTS")
    print("="*60)

    tests = [
        {
            'name': 'HEAD /',
            'event': {
                'path': '/prod/',
                'httpMethod': 'HEAD',
                'headers': {},
                'body': None
            }
        },
        {
            'name': 'HEAD /api/presets',
            'event': {
                'path': '/prod/api/presets',
                'httpMethod': 'HEAD',
                'headers': {},
                'body': None
            }
        },
        {
            'name': 'HEAD /presets',
            'event': {
                'path': '/prod/presets',
                'httpMethod': 'HEAD',
                'headers': {},
                'body': None
            }
        },
        {
            'name': 'HEAD /evaluate',
            'event': {
                'path': '/prod/evaluate',
                'httpMethod': 'HEAD',
                'headers': {},
                'body': None
            }
        },
        {
            'name': 'GET / (control test)',
            'event': {
                'path': '/prod/',
                'httpMethod': 'GET',
                'headers': {},
                'body': None
            }
        },
        {
            'name': 'GET /api/presets (control test)',
            'event': {
                'path': '/prod/api/presets',
                'httpMethod': 'GET',
                'headers': {},
                'body': None
            }
        }
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n{test['name']}:")
        print(f"  Path: {test['event']['path']}")
        print(f"  Method: {test['event']['httpMethod']}")

        try:
            response = handler(test['event'], None)
            status = response.get('statusCode')
            headers = response.get('headers', {})
            body = response.get('body', '')

            print(f"  ✅ Status: {status}")
            print(f"  Headers: {list(headers.keys())}")

            # For HEAD requests, body should be empty
            if test['event']['httpMethod'] == 'HEAD':
                if body == '':
                    print(f"  ✅ Body is empty (correct for HEAD)")
                else:
                    print(f"  ❌ Body should be empty for HEAD but got: {len(body)} characters")
                    failed += 1
                    continue

            # Check that we got 200
            if status == 200:
                print(f"  ✅ Response OK")
                passed += 1
            else:
                print(f"  ❌ Expected 200 but got {status}")
                failed += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0

if __name__ == "__main__":
    success = test_head_requests()
    sys.exit(0 if success else 1)
