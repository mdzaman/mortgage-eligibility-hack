#!/usr/bin/env python3

import requests
import json

def test_deployed_fedti():
    """Test that the deployed API returns FEDTI correctly"""
    
    api_url = "https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/api/evaluate"
    
    test_data = {
        'credit_score': 760,
        'gross_monthly_income': 10000,
        'monthly_debts': 650,
        'num_financed_properties': 1,
        'first_time_homebuyer': False,
        'owns_property_last_3yrs': True,
        'liquid_assets': 50000,
        'ami_ratio': '',
        'purchase_price': 400000,
        'appraised_value': 400000,
        'units': 1,
        'property_type': 'SFR',
        'occupancy': 'primary',
        'condition_rating': 'C3',
        'is_high_cost_area': True,
        'loan_amount': 300000,
        'note_rate': 6.50,
        'term_months': 360,
        'purpose': 'purchase',
        'mi_type': '',
        'mi_coverage_pct': ''
    }
    
    print("=== Testing Deployed API for FEDTI ===")
    print(f"API URL: {api_url}")
    
    try:
        response = requests.post(
            api_url,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            metrics = result.get('calculated_metrics', {})
            
            print(f"LTV: {metrics.get('LTV', 'N/A')}")
            print(f"DTI: {metrics.get('DTI', 'N/A')}")
            print(f"FEDTI: {metrics.get('FEDTI', 'N/A')}")
            
            if 'FEDTI' in metrics and metrics['FEDTI'] != 'N/A':
                print(f"✓ Deployed API returns FEDTI: {metrics['FEDTI']}")
                return True
            else:
                print("✗ Deployed API missing FEDTI in response")
                print(f"Full response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"✗ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_deployed_fedti()
    exit(0 if success else 1)
