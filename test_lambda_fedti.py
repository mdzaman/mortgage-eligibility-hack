#!/usr/bin/env python3

import sys
import os
import json
sys.path.append('/home/coder/mortgage-eligibility-hack/genai-mortgage-hack')

from lambda_handler import handler

def test_lambda_fedti():
    """Test that lambda handler returns FEDTI in the response"""
    
    # Create test event
    event = {
        'path': '/api/evaluate',
        'httpMethod': 'POST',
        'body': json.dumps({
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
        })
    }
    
    context = {}
    
    # Call lambda handler
    response = handler(event, context)
    
    print("=== Lambda FEDTI Test ===")
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        metrics = body.get('calculated_metrics', {})
        
        print(f"LTV: {metrics.get('LTV', 'N/A')}")
        print(f"DTI: {metrics.get('DTI', 'N/A')}")
        print(f"FEDTI: {metrics.get('FEDTI', 'N/A')}")
        
        if 'FEDTI' in metrics and metrics['FEDTI'] != 'N/A':
            print(f"✓ Lambda handler returns FEDTI: {metrics['FEDTI']}")
            return True
        else:
            print("✗ Lambda handler missing FEDTI in response")
            return False
    else:
        print(f"✗ Lambda handler error: {response.get('body', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_lambda_fedti()
    sys.exit(0 if success else 1)
