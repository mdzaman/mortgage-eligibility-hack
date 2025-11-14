#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/coder/mortgage-eligibility-hack/genai-mortgage-hack')

from mortgage_engine import (
    price_scenario,
    ScenarioInput,
    BorrowerProfile,
    PropertyProfile,
    LoanTerms,
    FinancingStructure
)

def test_fedti_calculation():
    """Test that FEDTI is properly calculated and returned"""
    
    # Create test scenario
    borrower = BorrowerProfile(
        credit_score=760,
        gross_monthly_income=10000,
        monthly_debts={"other_debts": 650},
        num_financed_properties=1,
        first_time_homebuyer=False,
        owns_property_last_3yrs=True,
        liquid_assets_after_closing=50000,
        doc_type="full",
        ami_ratio=None
    )

    property_info = PropertyProfile(
        purchase_price=400000,
        appraised_value=400000,
        units=1,
        property_type='SFR',
        occupancy='primary',
        condition_rating='C3',
        state='CA',
        county='Unknown',
        is_high_cost_area=True
    )

    loan = LoanTerms(
        loan_amount=300000,
        note_rate=6.50,
        term_months=360,
        arm=False,
        purpose='purchase',
        product_type='fixed',
        channel='conforming'
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

    # Run the engine
    result = price_scenario(scenario)
    
    # Check if FEDTI is calculated
    print("=== FEDTI Fix Test ===")
    print(f"Eligibility: {result.eligibility_overall}")
    print(f"LTV: {result.calculated_metrics.get('LTV', 0):.2%}")
    print(f"DTI: {result.calculated_metrics.get('DTI', 0):.2%}")
    print(f"FEDTI: {result.calculated_metrics.get('FEDTI', 0):.2%}")
    
    # Verify FEDTI exists and is not zero
    fedti = result.calculated_metrics.get('FEDTI', 0)
    if fedti > 0:
        print(f"✓ FEDTI calculation successful: {fedti:.2%}")
        return True
    else:
        print("✗ FEDTI calculation failed - value is 0 or missing")
        return False

if __name__ == "__main__":
    success = test_fedti_calculation()
    sys.exit(0 if success else 1)
