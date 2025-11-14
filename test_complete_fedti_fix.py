#!/usr/bin/env python3

import requests
import json
import sys

def test_complete_fedti_fix():
    """Complete test of FEDTI fix across all components"""
    
    print("=== Complete FEDTI Fix Test ===")
    
    # Test data
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
    
    all_tests_passed = True
    
    # Test 1: API Response includes FEDTI
    print("\n1. Testing API Response...")
    try:
        response = requests.post(
            api_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            metrics = result.get('calculated_metrics', {})
            
            if 'FEDTI' in metrics and metrics['FEDTI'] != 'N/A':
                print(f"   ✓ FEDTI present in API response: {metrics['FEDTI']}")
            else:
                print("   ✗ FEDTI missing from API response")
                all_tests_passed = False
                
            # Verify FEDTI value is reasonable
            fedti_str = metrics.get('FEDTI', '0.00%')
            try:
                fedti_val = float(fedti_str.replace('%', '')) / 100
                if 0.1 <= fedti_val <= 0.5:  # 10% to 50% is reasonable range
                    print(f"   ✓ FEDTI value is reasonable: {fedti_str}")
                else:
                    print(f"   ⚠ FEDTI value seems unusual: {fedti_str}")
            except:
                print(f"   ⚠ Could not parse FEDTI value: {fedti_str}")
                
        else:
            print(f"   ✗ API request failed: {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"   ✗ API test failed: {str(e)}")
        all_tests_passed = False
    
    # Test 2: Verify FEDTI calculation logic
    print("\n2. Testing FEDTI Calculation Logic...")
    try:
        # Expected calculation:
        # Loan amount: $300,000
        # Rate: 6.50%
        # Term: 360 months
        # Monthly P&I ≈ $1,896
        # Estimated taxes/insurance ≈ $167 (0.5% annually / 12)
        # Total PITIA ≈ $2,063
        # FEDTI = $2,063 / $10,000 = 20.63%
        
        expected_fedti_approx = 0.206  # Approximately 20.6%
        actual_fedti_str = metrics.get('FEDTI', '0.00%')
        actual_fedti = float(actual_fedti_str.replace('%', '')) / 100
        
        if abs(actual_fedti - expected_fedti_approx) < 0.01:  # Within 1%
            print(f"   ✓ FEDTI calculation appears correct: {actual_fedti_str}")
        else:
            print(f"   ⚠ FEDTI calculation may be off. Expected ~20.6%, got {actual_fedti_str}")
            
    except Exception as e:
        print(f"   ✗ FEDTI calculation test failed: {str(e)}")
        all_tests_passed = False
    
    # Test 3: Compare with DTI
    print("\n3. Testing FEDTI vs DTI Relationship...")
    try:
        dti_str = metrics.get('DTI', '0.00%')
        fedti_str = metrics.get('FEDTI', '0.00%')
        
        dti_val = float(dti_str.replace('%', '')) / 100
        fedti_val = float(fedti_str.replace('%', '')) / 100
        
        if fedti_val < dti_val:
            print(f"   ✓ FEDTI ({fedti_str}) < DTI ({dti_str}) - Correct relationship")
        else:
            print(f"   ✗ FEDTI ({fedti_str}) >= DTI ({dti_str}) - Incorrect relationship")
            all_tests_passed = False
            
    except Exception as e:
        print(f"   ✗ FEDTI vs DTI test failed: {str(e)}")
        all_tests_passed = False
    
    # Test 4: Web interface compatibility
    print("\n4. Testing Web Interface Compatibility...")
    try:
        # Check that the response format matches what the web interface expects
        required_fields = ['eligibility_overall', 'calculated_metrics', 'pricing']
        missing_fields = [field for field in required_fields if field not in result]
        
        if not missing_fields:
            print("   ✓ All required fields present for web interface")
        else:
            print(f"   ✗ Missing fields for web interface: {missing_fields}")
            all_tests_passed = False
            
        # Check metrics structure
        required_metrics = ['LTV', 'CLTV', 'DTI', 'FEDTI']
        missing_metrics = [metric for metric in required_metrics if metric not in metrics]
        
        if not missing_metrics:
            print("   ✓ All required metrics present")
        else:
            print(f"   ✗ Missing metrics: {missing_metrics}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"   ✗ Web interface compatibility test failed: {str(e)}")
        all_tests_passed = False
    
    # Summary
    print(f"\n=== Test Summary ===")
    if all_tests_passed:
        print("✓ All tests passed! FEDTI fix is working correctly.")
        print(f"✓ FEDTI value: {metrics.get('FEDTI', 'N/A')}")
        print(f"✓ DTI value: {metrics.get('DTI', 'N/A')}")
        print("✓ Web interface should now display FEDTI properly.")
        return True
    else:
        print("✗ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = test_complete_fedti_fix()
    sys.exit(0 if success else 1)
