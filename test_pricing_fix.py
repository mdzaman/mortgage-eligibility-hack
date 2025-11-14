#!/usr/bin/env python3
"""
Test script to verify pricing calculations are working correctly
"""

import sys
import os
import json
sys.path.append('/home/coder/mortgage-eligibility-hack/genai-mortgage-hack')

from mortgage_engine import (
    ScenarioInput,
    BorrowerProfile,
    PropertyProfile,
    LoanTerms,
    FinancingStructure,
    price_scenario
)
from lambda_handler import handler

def test_pricing_calculation():
    """Test that pricing calculations return proper values"""
    print("Testing pricing calculation...")
    
    # Create a scenario that should have some LLPA adjustments
    borrower = BorrowerProfile(
        credit_score=680,  # Lower credit score for LLPA
        gross_monthly_income=8000,
        monthly_debts={"other_debts": 1200},
        num_financed_properties=1,
        first_time_homebuyer=False,
        owns_property_last_3yrs=True,
        liquid_assets_after_closing=30000,
        doc_type="full"
    )

    property_info = PropertyProfile(
        appraised_value=400000,
        units=1,
        property_type="SFR",
        occupancy="primary",
        condition_rating="C3",
        state="CA",
        county="Unknown",
        is_high_cost_area=True
    )

    loan = LoanTerms(
        loan_amount=360000,  # Higher LTV for LLPA
        note_rate=6.50,
        term_months=360,
        arm=False,
        purpose="purchase",
        product_type="fixed",
        channel="conforming"
    )

    financing = FinancingStructure(
        subordinate_liens=[],
        mi_type=None,
        mi_coverage_pct=None
    )

    scenario = ScenarioInput(
        borrower=borrower,
        property=property_info,
        loan=loan,
        financing=financing
    )

    result = price_scenario(scenario)
    
    print(f"Base Rate: {result.pricing.base_rate:.3f}%")
    print(f"LLPA Total (bps): {result.pricing.llpa_total_bps:.2f}")
    print(f"LLPA Total (%): {result.pricing.llpa_total_bps / 100:.3f}%")
    print(f"Final Rate: {result.pricing.base_rate + (result.pricing.llpa_total_bps / 100):.3f}%")
    print(f"Components: {len(result.pricing.components)}")
    
    for component in result.pricing.components:
        print(f"  - {component.name}: {component.value_bps:.2f} bps ({component.reason})")
    
    return result

def test_lambda_response():
    """Test that lambda handler returns correct pricing fields"""
    print("\nTesting lambda handler response...")
    
    # Create test event
    test_data = {
        'credit_score': 680,
        'gross_monthly_income': 8000,
        'monthly_debts': 1200,
        'num_financed_properties': 1,
        'first_time_homebuyer': False,
        'owns_property_last_3yrs': True,
        'liquid_assets': 30000,
        'appraised_value': 400000,
        'units': 1,
        'property_type': 'SFR',
        'occupancy': 'primary',
        'condition_rating': 'C3',
        'is_high_cost_area': True,
        'loan_amount': 360000,
        'note_rate': 6.50,
        'term_months': 360,
        'purpose': 'purchase'
    }
    
    event = {
        'path': '/api/evaluate',
        'httpMethod': 'POST',
        'body': json.dumps(test_data)
    }
    
    response = handler(event, {})
    
    if response['statusCode'] == 200:
        result = json.loads(response['body'])
        pricing = result.get('pricing', {})
        
        print("Lambda Response Pricing Fields:")
        print(f"  base_rate: {pricing.get('base_rate', 'MISSING')}")
        print(f"  total_llpa: {pricing.get('total_llpa', 'MISSING')}")
        print(f"  final_rate: {pricing.get('final_rate', 'MISSING')}")
        print(f"  rate_differential: {pricing.get('rate_differential', 'MISSING')}")
        print(f"  llpa_components: {len(pricing.get('llpa_components', []))} components")
        
        # Check if all required fields are present and not undefined
        required_fields = ['base_rate', 'total_llpa', 'final_rate', 'rate_differential']
        missing_fields = [field for field in required_fields if pricing.get(field) is None]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All required pricing fields present")
            
        return result
    else:
        print(f"❌ Lambda error: {response}")
        return None

if __name__ == "__main__":
    engine_result = test_pricing_calculation()
    lambda_result = test_lambda_response()
    
    print(f"\nEligibility: {engine_result.eligibility_overall}")
    print("Pricing fix test completed!")
