#!/usr/bin/env python3
"""
Test script to verify occupancy and purpose validation fixes
"""

import sys
import os
sys.path.append('/home/coder/mortgage-eligibility-hack/genai-mortgage-hack')

from mortgage_engine import (
    ScenarioInput,
    BorrowerProfile,
    PropertyProfile,
    LoanTerms,
    FinancingStructure,
    price_scenario
)

def test_occupancy_validation():
    """Test that occupancy validation works with correct values"""
    print("Testing occupancy validation...")
    
    # Test valid occupancy values
    valid_occupancies = ["primary", "second_home", "investment"]
    
    for occupancy in valid_occupancies:
        borrower = BorrowerProfile(
            credit_score=760,
            gross_monthly_income=10000,
            monthly_debts={"other_debts": 650},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=50000,
            doc_type="full"
        )

        property_info = PropertyProfile(
            appraised_value=400000,
            units=1,
            property_type="SFR",
            occupancy=occupancy,
            condition_rating="C3",
            state="CA",
            county="Unknown",
            is_high_cost_area=True
        )

        loan = LoanTerms(
            loan_amount=300000,
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
        
        # Check if occupancy rule passed
        occupancy_rule = next((r for r in result.rule_results if r.rule_name == "OCCUPANCY"), None)
        if occupancy_rule and occupancy_rule.eligible:
            print(f"  ✓ {occupancy} occupancy: PASSED")
        else:
            print(f"  ✗ {occupancy} occupancy: FAILED - {occupancy_rule.messages if occupancy_rule else 'Rule not found'}")

def test_purpose_validation():
    """Test that purpose validation works with correct values"""
    print("\nTesting purpose validation...")
    
    # Test valid purpose values
    valid_purposes = ["purchase", "rate_term_refi", "cash_out_refi"]
    
    for purpose in valid_purposes:
        borrower = BorrowerProfile(
            credit_score=760,
            gross_monthly_income=10000,
            monthly_debts={"other_debts": 650},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=50000,
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
            loan_amount=300000,
            note_rate=6.50,
            term_months=360,
            arm=False,
            purpose=purpose,
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
        
        # Check if purpose rule passed
        purpose_rule = next((r for r in result.rule_results if r.rule_name == "LOAN_PURPOSE"), None)
        if purpose_rule and purpose_rule.eligible:
            print(f"  ✓ {purpose} purpose: PASSED")
        else:
            print(f"  ✗ {purpose} purpose: FAILED - {purpose_rule.messages if purpose_rule else 'Rule not found'}")

def test_invalid_values():
    """Test that invalid values are properly rejected"""
    print("\nTesting invalid values...")
    
    # Test invalid occupancy
    try:
        borrower = BorrowerProfile(
            credit_score=760,
            gross_monthly_income=10000,
            monthly_debts={"other_debts": 650},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=50000,
            doc_type="full"
        )

        property_info = PropertyProfile(
            appraised_value=400000,
            units=1,
            property_type="SFR",
            occupancy="Primary",  # Wrong case
            condition_rating="C3",
            state="CA",
            county="Unknown",
            is_high_cost_area=True
        )

        loan = LoanTerms(
            loan_amount=300000,
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
        occupancy_rule = next((r for r in result.rule_results if r.rule_name == "OCCUPANCY"), None)
        if occupancy_rule and not occupancy_rule.eligible:
            print(f"  ✓ Invalid occupancy 'Primary' properly rejected: {occupancy_rule.messages}")
        else:
            print(f"  ✗ Invalid occupancy 'Primary' was not rejected")
    except Exception as e:
        print(f"  ✓ Invalid occupancy 'Primary' caused exception: {e}")

if __name__ == "__main__":
    test_occupancy_validation()
    test_purpose_validation()
    test_invalid_values()
    print("\nValidation tests completed!")
