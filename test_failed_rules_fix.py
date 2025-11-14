#!/usr/bin/env python3
"""
Test script to verify that failed rules are now displaying properly
instead of showing [object Object]
"""

import requests
import json

# API endpoint from the deployment
API_URL = "https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod/api/evaluate"

def test_failed_rules_display():
    """Test with a scenario that will fail multiple rules"""
    
    # Create a scenario that will fail multiple rules
    test_data = {
        "credit_score": 500,  # Too low
        "gross_monthly_income": 3000,
        "monthly_debts": 2000,  # High DTI
        "num_financed_properties": 1,
        "first_time_homebuyer": False,
        "owns_property_last_3yrs": True,
        "liquid_assets": 5000,  # Low reserves
        "ami_ratio": "",
        "purchase_price": 500000,
        "appraised_value": 500000,
        "units": 1,
        "property_type": "SFR",
        "occupancy": "primary",
        "condition_rating": "C3",
        "is_high_cost_area": True,
        "loan_amount": 475000,  # High LTV (95%)
        "note_rate": 7.50,
        "term_months": 360,
        "purpose": "purchase",
        "mi_type": "",
        "mi_coverage_pct": ""
    }
    
    print("Testing mortgage eligibility with scenario designed to fail multiple rules...")
    print(f"API URL: {API_URL}")
    
    try:
        response = requests.post(
            API_URL,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            json=test_data,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Eligibility Overall: {result.get('eligibility_overall')}")
            
            # Check failed rules structure
            failed_rules = result.get('failed_rules', [])
            print(f"\nNumber of failed rules: {len(failed_rules)}")
            
            if failed_rules:
                print("\nFailed Rules (should show rule names and messages, not [object Object]):")
                for i, rule in enumerate(failed_rules, 1):
                    if isinstance(rule, dict):
                        rule_name = rule.get('rule_name', 'Unknown')
                        messages = rule.get('messages', [])
                        print(f"  {i}. {rule_name}: {', '.join(messages)}")
                    else:
                        print(f"  {i}. ERROR: Rule is not a dict: {rule}")
            
            # Check all rules structure
            all_rules = result.get('all_rules', [])
            print(f"\nTotal rules evaluated: {len(all_rules)}")
            
            if all_rules:
                print("\nAll Rules Summary:")
                for rule in all_rules:
                    if isinstance(rule, dict):
                        rule_name = rule.get('rule_name', 'Unknown')
                        eligible = rule.get('eligible', False)
                        status = "✓ PASS" if eligible else "✗ FAIL"
                        print(f"  {status} {rule_name}")
                    else:
                        print(f"  ERROR: Rule is not a dict: {rule}")
            
            print("\n" + "="*60)
            print("SUCCESS: Failed rules are now properly structured!")
            print("The web app should now display rule names and messages")
            print("instead of '[object Object]'")
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_failed_rules_display()
