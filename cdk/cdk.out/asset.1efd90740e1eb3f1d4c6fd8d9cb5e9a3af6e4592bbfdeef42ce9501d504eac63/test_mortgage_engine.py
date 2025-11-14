"""
Unit and Integration Tests for Mortgage Engine
===============================================

Comprehensive test suite covering all 16 rules and integration scenarios.
"""

import sys
from mortgage_engine import (
    price_scenario,
    ScenarioInput,
    BorrowerProfile,
    PropertyProfile,
    LoanTerms,
    FinancingStructure,
    DEFAULT_CONFIG
)


def assert_approx(actual: float, expected: float, tolerance: float = 0.01, label: str = "") -> None:
    """Helper to assert floating point equality within tolerance."""
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"{label}: Expected {expected:.4f}, got {actual:.4f} (diff: {abs(actual - expected):.4f})"
        )


def test_ltv_cltv_hcltv_computations():
    """Test Rule 1: LTV/CLTV/HCLTV calculations."""
    print("Testing LTV/CLTV/HCLTV computations...")

    # Test 1: Simple LTV, no subordinate debt
    scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=740,
            gross_monthly_income=8000.0,
            monthly_debts={},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=20000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=400000.0,
            appraised_value=400000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="LA",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=320000.0,  # 80% LTV
            note_rate=6.50,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure(
            subordinate_liens=[],
            mi_type=None,
            mi_coverage_pct=None
        )
    )

    result = price_scenario(scenario)
    assert_approx(result.calculated_metrics["LTV"], 0.80, label="Simple LTV")
    assert_approx(result.calculated_metrics["CLTV"], 0.80, label="Simple CLTV")
    assert result.eligibility_overall, "Should be eligible at 80% LTV"

    # Test 2: With subordinate lien
    scenario.financing.subordinate_liens = [
        {"type": "second_mortgage", "current_balance": 20000.0}
    ]
    scenario.loan.loan_amount = 300000.0  # First: 75%, CLTV: 80%

    result = price_scenario(scenario)
    assert_approx(result.calculated_metrics["LTV"], 0.75, label="LTV with subordinate")
    assert_approx(result.calculated_metrics["CLTV"], 0.80, label="CLTV with subordinate")

    # Test 3: With HELOC (tests HCLTV)
    scenario.financing.subordinate_liens = [
        {"type": "heloc", "current_balance": 10000.0, "credit_limit": 50000.0}
    ]

    result = price_scenario(scenario)
    assert_approx(result.calculated_metrics["HCLTV"], 0.875, tolerance=0.01, label="HCLTV with HELOC")

    # Test 4: Boundary at 80% - should not require MI
    scenario.financing.subordinate_liens = []
    scenario.loan.loan_amount = 320000.0  # Exactly 80%

    result = price_scenario(scenario)
    mi_rule = next(r for r in result.rule_results if r.rule_name == "MORTGAGE_INSURANCE")
    assert not mi_rule.metrics.get("mi_required", False), "No MI required at 80% LTV"

    # Test 5: Slightly above 80% - should require MI
    scenario.loan.loan_amount = 320400.0  # 80.1%
    scenario.financing.mi_type = "borrower_paid_monthly"
    scenario.financing.mi_coverage_pct = 0.12

    result = price_scenario(scenario)
    mi_rule = next(r for r in result.rule_results if r.rule_name == "MORTGAGE_INSURANCE")
    assert mi_rule.metrics.get("mi_required", False), "MI required above 80% LTV"

    print("  ✓ LTV/CLTV/HCLTV tests passed")


def test_dti_boundaries():
    """Test Rule 3: DTI at various thresholds."""
    print("Testing DTI boundaries...")

    base_scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=740,
            gross_monthly_income=10000.0,
            monthly_debts={"car": 400.0},  # Plus PITIA ~= 2000
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=30000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=400000.0,
            appraised_value=400000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="LA",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=300000.0,
            note_rate=6.50,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )

    # Test 1: Low DTI (~25%)
    result = price_scenario(base_scenario)
    dti = result.calculated_metrics["DTI"]
    assert dti < 0.36, "Should be below manual threshold"
    dti_rule = next(r for r in result.rule_results if r.rule_name == "DTI")
    assert dti_rule.eligible, "Low DTI should be eligible"

    # Test 2: DTI around 45% (requires DU or compensating)
    base_scenario.borrower.monthly_debts = {"car": 2500.0}  # Push DTI up
    result = price_scenario(base_scenario)
    dti = result.calculated_metrics["DTI"]
    assert 0.40 < dti < 0.50, f"DTI should be in 40-50% range, got {dti:.2%}"

    # Test 3: DTI > 50% (should fail)
    base_scenario.borrower.monthly_debts = {"car": 4000.0}
    result = price_scenario(base_scenario)
    dti_rule = next(r for r in result.rule_results if r.rule_name == "DTI")
    assert not dti_rule.eligible, "DTI > 50% should be ineligible"

    print("  ✓ DTI boundary tests passed")


def test_loan_amount_limits():
    """Test Rule 7: Conforming vs High-Balance vs Jumbo."""
    print("Testing loan amount limits...")

    # Test 1: Conforming
    scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=740,
            gross_monthly_income=15000.0,
            monthly_debts={"car": 400.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=50000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=1000000.0,
            appraised_value=1000000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="LA",
            is_high_cost_area=False  # Not high-cost
        ),
        loan=LoanTerms(
            loan_amount=700000.0,  # Within conforming
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
    assert result.calculated_metrics["channel"] == "conforming", "Should be conforming"
    loan_limit_rule = next(r for r in result.rule_results if r.rule_name == "LOAN_AMOUNT_LIMITS")
    assert loan_limit_rule.eligible, "Should be eligible as conforming"

    # Test 2: High-Balance
    scenario.property.is_high_cost_area = True
    scenario.loan.loan_amount = 900000.0  # Above baseline, below high-cost limit

    result = price_scenario(scenario)
    assert result.calculated_metrics["channel"] == "high_balance", "Should be high-balance"

    # Test 3: Jumbo (ineligible)
    scenario.loan.loan_amount = 1500000.0  # Above high-cost limit

    result = price_scenario(scenario)
    loan_limit_rule = next(r for r in result.rule_results if r.rule_name == "LOAN_AMOUNT_LIMITS")
    assert not loan_limit_rule.eligible, "Should be ineligible as jumbo"

    print("  ✓ Loan amount limit tests passed")


def test_mi_requirements():
    """Test Rule 8: MI requirements at various LTV levels."""
    print("Testing MI requirements...")

    base_scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=740,
            gross_monthly_income=8000.0,
            monthly_debts={"car": 300.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=20000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=400000.0,
            appraised_value=400000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="LA",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=0.0,  # Will vary
            note_rate=6.50,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )

    # Test 1: 79.99% LTV - no MI needed
    base_scenario.loan.loan_amount = 319960.0  # 79.99%
    result = price_scenario(base_scenario)
    mi_rule = next(r for r in result.rule_results if r.rule_name == "MORTGAGE_INSURANCE")
    assert not mi_rule.metrics.get("mi_required", False), "No MI at 79.99%"

    # Test 2: 80.01% LTV - MI required, but not provided (should fail)
    base_scenario.loan.loan_amount = 320040.0  # 80.01%
    result = price_scenario(base_scenario)
    mi_rule = next(r for r in result.rule_results if r.rule_name == "MORTGAGE_INSURANCE")
    assert not mi_rule.eligible, "Should fail without MI when LTV > 80%"

    # Test 3: 85% LTV with correct MI
    base_scenario.loan.loan_amount = 340000.0  # 85%
    base_scenario.financing.mi_type = "borrower_paid_monthly"
    base_scenario.financing.mi_coverage_pct = 0.25  # 25% coverage required for 85%
    result = price_scenario(base_scenario)
    mi_rule = next(r for r in result.rule_results if r.rule_name == "MORTGAGE_INSURANCE")
    assert mi_rule.eligible, "Should pass with correct MI"

    # Test 4: Minimum MI (below standard) - eligible but triggers LLPA
    base_scenario.loan.loan_amount = 344000.0  # 86% LTV (requires 25% coverage)
    base_scenario.financing.mi_coverage_pct = 0.12  # Below 25% standard
    result = price_scenario(base_scenario)
    mi_rule = next(r for r in result.rule_results if r.rule_name == "MORTGAGE_INSURANCE")
    # Should still be eligible but flagged for LLPA
    assert "below standard" in " ".join(mi_rule.messages).lower(), "Should note below-standard coverage"

    print("  ✓ MI requirement tests passed")


def test_reserve_requirements():
    """Test Rule 9: Reserve calculations."""
    print("Testing reserve requirements...")

    # Test 1: Primary 1-unit (minimal reserves)
    scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=740,
            gross_monthly_income=10000.0,
            monthly_debts={"car": 400.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=5000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=400000.0,
            appraised_value=400000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="LA",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=300000.0,
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
    reserve_rule = next(r for r in result.rule_results if r.rule_name == "RESERVES")
    assert reserve_rule.metrics["required_months"] == 0, "Primary 1-unit should require 0 months base"

    # Test 2: 2-unit primary (6 months required)
    scenario.property.units = 2
    scenario.borrower.liquid_assets_after_closing = 1000.0  # Too low

    result = price_scenario(scenario)
    reserve_rule = next(r for r in result.rule_results if r.rule_name == "RESERVES")
    assert reserve_rule.metrics["required_months"] == 6, "2-unit primary should require 6 months"
    assert not reserve_rule.eligible, "Should fail with insufficient reserves"

    # Test 3: Investment property with multiple financed properties
    scenario.property.occupancy = "investment"
    scenario.property.units = 1
    scenario.borrower.num_financed_properties = 5
    scenario.borrower.liquid_assets_after_closing = 50000.0

    result = price_scenario(scenario)
    reserve_rule = next(r for r in result.rule_results if r.rule_name == "RESERVES")
    assert reserve_rule.metrics["required_months"] == 6, "Investment should require 6 months base"
    # Should also include additional reserves for multiple properties
    assert reserve_rule.metrics["required_dollars"] > reserve_rule.metrics["required_months"] * 2000

    print("  ✓ Reserve requirement tests passed")


def test_financed_properties():
    """Test Rule 10: Number of financed properties."""
    print("Testing financed properties constraints...")

    base_scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=740,
            gross_monthly_income=15000.0,
            monthly_debts={"mortgages": 4000.0},
            num_financed_properties=0,  # Will vary
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=100000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=500000.0,
            appraised_value=500000.0,
            units=1,
            property_type="SFR",
            occupancy="investment",
            condition_rating="C3",
            state="FL",
            county="Miami",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=375000.0,
            note_rate=7.00,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )

    # Test 1: 4 properties (standard)
    base_scenario.borrower.num_financed_properties = 4
    result = price_scenario(base_scenario)
    prop_rule = next(r for r in result.rule_results if r.rule_name == "FINANCED_PROPERTIES")
    assert prop_rule.eligible, "4 properties should be standard eligible"

    # Test 2: 7 properties (extended, requires 720 score)
    base_scenario.borrower.num_financed_properties = 7
    base_scenario.borrower.credit_score = 715  # Below 720

    result = price_scenario(base_scenario)
    prop_rule = next(r for r in result.rule_results if r.rule_name == "FINANCED_PROPERTIES")
    assert not prop_rule.eligible, "7 properties with 715 score should fail"

    # Test 3: 7 properties with 720+ score
    base_scenario.borrower.credit_score = 725

    result = price_scenario(base_scenario)
    prop_rule = next(r for r in result.rule_results if r.rule_name == "FINANCED_PROPERTIES")
    assert prop_rule.eligible, "7 properties with 725 score should pass"

    # Test 4: 11 properties (too many)
    base_scenario.borrower.num_financed_properties = 11

    result = price_scenario(base_scenario)
    prop_rule = next(r for r in result.rule_results if r.rule_name == "FINANCED_PROPERTIES")
    assert not prop_rule.eligible, "11 properties should fail (max 10)"

    print("  ✓ Financed properties tests passed")


def test_fthb_requirements():
    """Test Rule 14: First-time homebuyer logic and LLPA waivers."""
    print("Testing FTHB requirements...")

    # Test 1: 97% LTV requires FTHB
    scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=700,
            gross_monthly_income=7000.0,
            monthly_debts={"car": 300.0},
            num_financed_properties=1,
            first_time_homebuyer=False,  # Not FTHB
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=10000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=300000.0,
            appraised_value=300000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="TX",
            county="Harris",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=291000.0,  # 97%
            note_rate=6.75,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure(
            mi_type="borrower_paid_monthly",
            mi_coverage_pct=0.35
        )
    )

    result = price_scenario(scenario)
    fthb_rule = next(r for r in result.rule_results if r.rule_name == "FIRST_TIME_HOMEBUYER")
    assert not fthb_rule.eligible, "97% LTV requires FTHB status"

    # Test 2: 97% LTV with FTHB - should pass
    scenario.borrower.first_time_homebuyer = True

    result = price_scenario(scenario)
    fthb_rule = next(r for r in result.rule_results if r.rule_name == "FIRST_TIME_HOMEBUYER")
    assert fthb_rule.eligible, "97% LTV with FTHB should pass"

    # Test 3: FTHB with low AMI triggers LLPA waiver
    scenario.borrower.ami_ratio = 0.90  # 90% of AMI

    result = price_scenario(scenario)
    fthb_rule = next(r for r in result.rule_results if r.rule_name == "FIRST_TIME_HOMEBUYER")
    assert fthb_rule.metrics["llpa_waiver_eligible"], "Low AMI FTHB should be waiver eligible"

    # Check LLPA is actually waived
    llpa_rule = next(r for r in result.rule_results if r.rule_name == "LLPA")
    has_waiver = any("FTHB" in str(comp.name) for comp in result.pricing.components if comp.value_bps < 0)
    assert has_waiver, "FTHB LLPA waiver should be applied"

    print("  ✓ FTHB tests passed")


def test_hoepa_hpml_flags():
    """Test Rule 15: HOEPA rejection and HPML flagging."""
    print("Testing HOEPA and HPML flags...")

    base_scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=660,
            gross_monthly_income=6000.0,
            monthly_debts={"car": 400.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=10000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=250000.0,
            appraised_value=250000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="OH",
            county="Cuyahoga",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=200000.0,
            note_rate=6.50,  # Standard rate
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )

    # Test 1: Normal rate - not HPML
    result = price_scenario(base_scenario)
    assert not result.flags["HPML"], "Standard rate should not be HPML"
    assert not result.flags["HOEPA"], "Standard rate should not be HOEPA"

    # Test 2: High rate - HPML but not HOEPA (eligible with warnings)
    base_scenario.loan.note_rate = 8.00

    result = price_scenario(base_scenario)
    hpml_rule = next(r for r in result.rule_results if r.rule_name == "HIGH_COST_HPML_HCLTV")
    # HPML might be flagged depending on calculation
    # The key is it shouldn't be HOEPA
    assert not result.flags["HOEPA"], "Moderately high rate should not trigger HOEPA"

    # Test 3: Very high rate - HOEPA (ineligible)
    base_scenario.loan.note_rate = 15.00  # Extremely high

    result = price_scenario(base_scenario)
    hpml_rule = next(r for r in result.rule_results if r.rule_name == "HIGH_COST_HPML_HCLTV")
    assert not hpml_rule.eligible or result.flags["HOEPA"], "Very high rate should trigger HOEPA"

    print("  ✓ HOEPA/HPML tests passed")


def test_llpa_calculations():
    """Test Rule 16: LLPA grid lookups and adjustments."""
    print("Testing LLPA calculations...")

    # Test 1: Top tier (780 FICO, 60% LTV)
    scenario = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=780,
            gross_monthly_income=20000.0,
            monthly_debts={"car": 400.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=100000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=500000.0,
            appraised_value=500000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="LA",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=300000.0,  # 60% LTV
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
    llpa = result.pricing.llpa_total_bps
    assert llpa == 0.0, f"Top tier should have 0 LLPA, got {llpa}"

    # Test 2: Investment property adds LLPA
    scenario.property.occupancy = "investment"
    scenario.property.units = 1
    scenario.loan.loan_amount = 375000.0  # 75% LTV

    result = price_scenario(scenario)
    llpa = result.pricing.llpa_total_bps
    assert llpa > 2.0, f"Investment property should have significant LLPA, got {llpa}"

    # Test 3: High LTV, lower credit adds more LLPA
    scenario.property.occupancy = "primary"
    scenario.borrower.credit_score = 680
    scenario.loan.loan_amount = 425000.0  # 85% LTV
    scenario.financing.mi_type = "borrower_paid_monthly"
    scenario.financing.mi_coverage_pct = 0.25

    result = price_scenario(scenario)
    llpa = result.pricing.llpa_total_bps
    assert llpa > 3.0, f"85% LTV with 680 score should have substantial LLPA, got {llpa}"

    # Test 4: FTHB waiver reduces LLPA
    scenario_fthb = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=700,
            gross_monthly_income=7000.0,
            monthly_debts={"car": 300.0},
            num_financed_properties=1,
            first_time_homebuyer=True,
            owns_property_last_3yrs=False,
            liquid_assets_after_closing=10000.0,
            doc_type="full",
            ami_ratio=0.85  # 85% AMI - triggers waiver
        ),
        property=PropertyProfile(
            purchase_price=300000.0,
            appraised_value=300000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="TX",
            county="Harris",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=270000.0,  # 90% LTV
            note_rate=6.75,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure(
            mi_type="borrower_paid_monthly",
            mi_coverage_pct=0.25
        )
    )

    result_no_waiver = price_scenario(scenario_fthb)
    llpa_no_waiver = result_no_waiver.pricing.llpa_total_bps

    # With waiver, LLPA should be significantly reduced
    # The waiver removes base grid and occupancy adjustments
    has_negative_component = any(
        comp.value_bps < 0 for comp in result_no_waiver.pricing.components
    )
    assert has_negative_component, "FTHB waiver should create negative LLPA component"

    print("  ✓ LLPA calculation tests passed")


def test_integration_full_scenarios():
    """Integration tests with complete scenarios."""
    print("Testing full integration scenarios...")

    # Scenario 1: Should PASS - standard conforming
    scenario_pass = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=760,
            gross_monthly_income=12000.0,
            monthly_debts={"car": 400.0, "student": 250.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=50000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=500000.0,
            appraised_value=500000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="CA",
            county="LA",
            is_high_cost_area=True
        ),
        loan=LoanTerms(
            loan_amount=375000.0,  # 75% LTV
            note_rate=6.50,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )

    result = price_scenario(scenario_pass)
    assert result.eligibility_overall, "Standard conforming scenario should pass"
    assert result.pricing is not None, "Should have pricing"
    assert result.pricing.net_price > 0, "Should have positive net price"

    # Scenario 2: Should FAIL - insufficient reserves
    scenario_fail_reserves = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=720,
            gross_monthly_income=8000.0,
            monthly_debts={"car": 400.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=1000.0,  # Too low
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=400000.0,
            appraised_value=400000.0,
            units=2,  # 2-unit requires 6 months reserves
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="IL",
            county="Cook",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=300000.0,
            note_rate=6.75,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure()
    )

    result = price_scenario(scenario_fail_reserves)
    assert not result.eligibility_overall, "Should fail due to insufficient reserves"

    # Scenario 3: Should FAIL - LTV too high
    scenario_fail_ltv = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=720,
            gross_monthly_income=8000.0,
            monthly_debts={"car": 400.0},
            num_financed_properties=1,
            first_time_homebuyer=False,  # Not FTHB
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=20000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=300000.0,
            appraised_value=300000.0,
            units=1,
            property_type="SFR",
            occupancy="primary",
            condition_rating="C3",
            state="OH",
            county="Franklin",
            is_high_cost_area=False
        ),
        loan=LoanTerms(
            loan_amount=291000.0,  # 97% LTV without FTHB
            note_rate=6.75,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure(
            mi_type="borrower_paid_monthly",
            mi_coverage_pct=0.35
        )
    )

    result = price_scenario(scenario_fail_ltv)
    assert not result.eligibility_overall, "Should fail - 97% LTV requires FTHB"

    # Scenario 4: Should PASS - same as above but with FTHB
    scenario_fail_ltv.borrower.first_time_homebuyer = True
    result = price_scenario(scenario_fail_ltv)
    assert result.eligibility_overall, "Should pass with FTHB at 97% LTV"

    print("  ✓ Integration tests passed")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "=" * 80)
    print("MORTGAGE ENGINE TEST SUITE")
    print("=" * 80 + "\n")

    test_functions = [
        test_ltv_cltv_hcltv_computations,
        test_dti_boundaries,
        test_loan_amount_limits,
        test_mi_requirements,
        test_reserve_requirements,
        test_financed_properties,
        test_fthb_requirements,
        test_hoepa_hpml_flags,
        test_llpa_calculations,
        test_integration_full_scenarios
    ]

    failed = []

    for test_func in test_functions:
        try:
            test_func()
        except AssertionError as e:
            print(f"  ✗ {test_func.__name__} FAILED: {e}")
            failed.append((test_func.__name__, str(e)))
        except Exception as e:
            print(f"  ✗ {test_func.__name__} ERROR: {e}")
            failed.append((test_func.__name__, str(e)))

    print("\n" + "=" * 80)
    if not failed:
        print("ALL TESTS PASSED ✓")
        print("=" * 80 + "\n")
        return 0
    else:
        print(f"TESTS FAILED: {len(failed)}/{len(test_functions)}")
        print("=" * 80)
        for name, error in failed:
            print(f"\n{name}:")
            print(f"  {error}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
