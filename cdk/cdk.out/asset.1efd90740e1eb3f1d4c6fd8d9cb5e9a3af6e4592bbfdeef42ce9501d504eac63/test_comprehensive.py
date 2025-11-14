#!/usr/bin/env python3
"""
Comprehensive Test Suite for Mortgage Engine Application
"""
import json
import http.client
import sys
from mortgage_engine import price_scenario, ScenarioInput, BorrowerProfile, PropertyProfile, LoanTerms, FinancingStructure

def test_engine_unit():
    """Test core engine functionality"""
    print("Testing mortgage engine core...")
    
    scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=760,
            gross_monthly_income=10000,
            monthly_debts={"other": 500},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=50000,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=400000,
            appraised_value=400000,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="Los Angeles",
            is_high_cost_area=True
        ),
        loan=LoanTerms(
            loan_amount=300000,
            note_rate=6.50,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )
    
    result = price_scenario(scenario)
    assert result.eligibility_overall, "Basic scenario should be eligible"
    assert result.calculated_metrics['LTV'] == 0.75, f"LTV should be 75%, got {result.calculated_metrics['LTV']}"
    print("  ✓ Engine unit test passed")

def test_api_endpoints():
    """Test HTTP API endpoints"""
    print("Testing API endpoints...")
    
    # Test homepage
    conn = http.client.HTTPConnection('localhost', 3000)
    conn.request('GET', '/')
    response = conn.getresponse()
    assert response.status == 200, f"Homepage failed: {response.status}"
    html = response.read().decode()
    assert 'Mortgage' in html, "Homepage should contain 'Mortgage'"
    conn.close()
    print("  ✓ Homepage test passed")
    
    # Test API evaluation
    test_data = {
        "credit_score": 760,
        "gross_monthly_income": 10000,
        "monthly_debts": 500,
        "num_financed_properties": 1,
        "first_time_homebuyer": False,
        "owns_property_last_3yrs": True,
        "liquid_assets": 50000,
        "appraised_value": 400000,
        "purchase_price": 400000,
        "units": 1,
        "property_type": "SFR",
        "occupancy": "primary",
        "loan_amount": 300000,
        "note_rate": 6.50,
        "purpose": "purchase"
    }
    
    conn = http.client.HTTPConnection('localhost', 3000)
    headers = {'Content-Type': 'application/json'}
    conn.request('POST', '/api/evaluate', json.dumps(test_data), headers)
    response = conn.getresponse()
    assert response.status == 200, f"API evaluation failed: {response.status}"
    
    result = json.loads(response.read().decode())
    assert result['eligibility_overall'], "API should return eligible result"
    assert 'calculated_metrics' in result, "API should return calculated metrics"
    conn.close()
    print("  ✓ API evaluation test passed")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("Testing edge cases...")
    
    # Test high DTI scenario
    scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=620,
            gross_monthly_income=5000,
            monthly_debts={"other": 3000},  # High DTI
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=10000,
            doc_type="full"
        ),
        property=PropertyProfile(
            appraised_value=300000,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="Los Angeles",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=250000,
            note_rate=7.00,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )
    
    result = price_scenario(scenario)
    # Should fail due to high DTI
    assert not result.eligibility_overall, "High DTI scenario should be ineligible"
    print("  ✓ High DTI rejection test passed")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("COMPREHENSIVE MORTGAGE ENGINE TEST SUITE")
    print("=" * 60)
    
    try:
        test_engine_unit()
        test_api_endpoints()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
