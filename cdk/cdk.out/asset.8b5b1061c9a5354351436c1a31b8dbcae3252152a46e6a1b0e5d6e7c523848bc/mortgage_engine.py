"""
Mortgage Eligibility and Pricing Engine
========================================

A self-contained engine for evaluating U.S. residential mortgage eligibility
and pricing based on Fannie Mae's 16 core eligibility dimensions.

Author: Senior Mortgage Technology Architect
Python 3.11+

This module implements:
- 16 Fannie Mae eligibility rule dimensions
- LLPA (Loan-Level Price Adjustment) pricing engine
- Configurable rule matrices and thresholds
- Full type hints and documentation

Usage:
    from mortgage_engine import price_scenario, ScenarioInput, BorrowerProfile, PropertyProfile, LoanTerms, FinancingStructure

    scenario = ScenarioInput(
        borrower=BorrowerProfile(...),
        property=PropertyProfile(...),
        loan=LoanTerms(...),
        financing=FinancingStructure(...)
    )

    result = price_scenario(scenario)
    print(f"Eligible: {result.eligibility_overall}")
    print(f"Net Price: {result.pricing.net_price}%")
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
import math


# ============================================================================
# README / USAGE GUIDE
# ============================================================================

README_TEXT = """
MORTGAGE ENGINE - USAGE GUIDE
==============================

OVERVIEW
--------
This engine evaluates residential mortgage scenarios against Fannie Mae's
16 core eligibility dimensions and computes pricing via LLPA adjustments.

QUICK START
-----------
1. Import the necessary classes:

   from mortgage_engine import (
       price_scenario, ScenarioInput,
       BorrowerProfile, PropertyProfile,
       LoanTerms, FinancingStructure
   )

2. Build a scenario:

   borrower = BorrowerProfile(
       credit_score=760,
       gross_monthly_income=10000.0,
       monthly_debts={"car": 400.0, "student": 200.0},
       num_financed_properties=1,
       first_time_homebuyer=False,
       owns_property_last_3yrs=True,
       liquid_assets_after_closing=50000.0,
       doc_type="full"
   )

   property_info = PropertyProfile(
       purchase_price=400000.0,
       appraised_value=400000.0,
       units=1,
       property_type="SFR",
       occupancy="primary",
       condition_rating="C3",
       state="CA",
       county="Los Angeles",
       is_high_cost_area=True,
       project_type=None
   )

   loan = LoanTerms(
       loan_amount=300000.0,
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
       mi_coverage_pct=None,
       base_rate_sheet_id="standard"
   )

   scenario = ScenarioInput(
       borrower=borrower,
       property=property_info,
       loan=loan,
       financing=financing
   )

3. Run the engine:

   result = price_scenario(scenario)

4. Check results:

   if result.eligibility_overall:
       print(f"APPROVED - Net Price: {result.pricing.net_price}%")
       print(f"Total LLPA: {result.pricing.llpa_total_bps} bps")
   else:
       print("DENIED - Reasons:")
       for rule in result.rule_results:
           if not rule.eligible:
               print(f"  - {rule.rule_name}: {', '.join(rule.messages)}")

5. Review detailed metrics:

   metrics = result.calculated_metrics
   print(f"LTV: {metrics['LTV']:.2%}")
   print(f"DTI: {metrics['DTI']:.2%}")
   print(f"Required Reserves: ${metrics['reserves_required_dollars']:,.2f}")

CONFIGURATION
-------------
All rule thresholds and LLPA matrices are defined in DEFAULT_CONFIG.
To customize, pass your own config dict to price_scenario():

   custom_config = DEFAULT_CONFIG.copy()
   custom_config['ltv_limits']['primary']['1_unit']['purchase'] = 0.90
   result = price_scenario(scenario, config=custom_config)

THE 16 ELIGIBILITY DIMENSIONS
------------------------------
1.  LTV/CLTV/HCLTV - Loan-to-Value ratios
2.  Credit Score - FICO requirements
3.  DTI - Debt-to-Income ratio
4.  Property Type - SFR, Condo, Co-op, Manufactured
5.  Occupancy - Primary, Second Home, Investment
6.  Loan Purpose - Purchase, Rate-Term Refi, Cash-Out Refi
7.  Loan Amount Limits - Conforming vs High-Balance
8.  Mortgage Insurance - Requirements when LTV > 80%
9.  Reserves - Liquid asset requirements
10. Financed Properties - Number of properties owned
11. Income Documentation - Full doc requirement
12. Property Condition - Appraisal acceptability
13. AUS vs Manual UW - DU vs Manual thresholds
14. First-Time Homebuyer - 97% LTV eligibility
15. High-Cost/HPML/HCLTV - HOEPA and HPML flags
16. LLPAs - Loan-Level Price Adjustments

NOTES
-----
- This is a simulation engine with simplified assumptions
- Real production systems should integrate actual DU findings
- LLPA matrices are approximations and should be replaced with current data
- All monetary values are in USD
- Percentages are decimals (0.80 = 80%)
"""


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class BorrowerProfile:
    """Borrower financial and demographic profile."""
    credit_score: int
    gross_monthly_income: float
    monthly_debts: Dict[str, float]
    num_financed_properties: int
    first_time_homebuyer: bool
    owns_property_last_3yrs: bool
    liquid_assets_after_closing: float
    doc_type: str = "full"  # "full", "non_qm"
    ami_ratio: Optional[float] = None  # borrower income / area median income


@dataclass
class PropertyProfile:
    """Property characteristics and location."""
    appraised_value: float
    units: int
    property_type: str  # "SFR", "Condo", "Coop", "Manufactured", "PUD", "MixedUse"
    occupancy: str  # "primary", "second_home", "investment"
    condition_rating: str  # "C1" through "C6"
    state: str
    county: str
    is_high_cost_area: bool
    purchase_price: Optional[float] = None
    project_type: Optional[str] = None


@dataclass
class LoanTerms:
    """Loan structure and terms."""
    loan_amount: float
    note_rate: float
    term_months: int
    arm: bool
    purpose: str  # "purchase", "rate_term_refi", "cash_out_refi"
    product_type: str  # "fixed", "arm"
    channel: str  # "conforming", "high_balance"


@dataclass
class FinancingStructure:
    """Financing details including subordinate debt and MI."""
    subordinate_liens: List[Dict[str, Any]] = field(default_factory=list)
    mi_type: Optional[str] = None  # "borrower_paid_monthly", "lender_paid", "single"
    mi_coverage_pct: Optional[float] = None
    base_rate_sheet_id: Optional[str] = "standard"


@dataclass
class ScenarioInput:
    """Complete mortgage scenario input."""
    borrower: BorrowerProfile
    property: PropertyProfile
    loan: LoanTerms
    financing: FinancingStructure


@dataclass
class RuleResult:
    """Result from a single eligibility rule."""
    rule_name: str
    eligible: bool
    messages: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PricingComponent:
    """Individual pricing adjustment component."""
    name: str
    value_bps: float  # basis points as percentage (100 bps = 1.00%)
    reason: str


@dataclass
class PricingResult:
    """Complete pricing result with LLPA breakdown."""
    base_rate: float
    base_price: float
    llpa_total_bps: float
    components: List[PricingComponent] = field(default_factory=list)
    waivers_applied: List[str] = field(default_factory=list)
    net_price: float = 0.0
    notes: List[str] = field(default_factory=list)


@dataclass
class EngineResult:
    """Complete engine evaluation result."""
    eligibility_overall: bool
    rule_results: List[RuleResult]
    pricing: Optional[PricingResult]
    calculated_metrics: Dict[str, Any] = field(default_factory=dict)
    flags: Dict[str, bool] = field(default_factory=dict)


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    # Rule 1: LTV/CLTV/HCLTV Limits
    # Structure: occupancy -> units -> purpose -> max_ltv/max_cltv
    "ltv_limits": {
        "primary": {
            "1_unit": {
                "purchase": {"max_ltv": 0.97, "max_cltv": 0.97, "max_hcltv": 0.97},
                "rate_term_refi": {"max_ltv": 0.97, "max_cltv": 0.97, "max_hcltv": 0.97},
                "cash_out_refi": {"max_ltv": 0.80, "max_cltv": 0.80, "max_hcltv": 0.90}
            },
            "2_unit": {
                "purchase": {"max_ltv": 0.85, "max_cltv": 0.85, "max_hcltv": 0.85},
                "rate_term_refi": {"max_ltv": 0.85, "max_cltv": 0.85, "max_hcltv": 0.85},
                "cash_out_refi": {"max_ltv": 0.75, "max_cltv": 0.75, "max_hcltv": 0.85}
            },
            "3_4_unit": {
                "purchase": {"max_ltv": 0.80, "max_cltv": 0.80, "max_hcltv": 0.80},
                "rate_term_refi": {"max_ltv": 0.80, "max_cltv": 0.80, "max_hcltv": 0.80},
                "cash_out_refi": {"max_ltv": 0.75, "max_cltv": 0.75, "max_hcltv": 0.85}
            }
        },
        "second_home": {
            "1_unit": {
                "purchase": {"max_ltv": 0.90, "max_cltv": 0.90, "max_hcltv": 0.90},
                "rate_term_refi": {"max_ltv": 0.90, "max_cltv": 0.90, "max_hcltv": 0.90},
                "cash_out_refi": {"max_ltv": 0.75, "max_cltv": 0.75, "max_hcltv": 0.85}
            }
        },
        "investment": {
            "1_unit": {
                "purchase": {"max_ltv": 0.85, "max_cltv": 0.85, "max_hcltv": 0.85},
                "rate_term_refi": {"max_ltv": 0.75, "max_cltv": 0.75, "max_hcltv": 0.85},
                "cash_out_refi": {"max_ltv": 0.75, "max_cltv": 0.75, "max_hcltv": 0.85}
            },
            "2_unit": {
                "purchase": {"max_ltv": 0.75, "max_cltv": 0.75, "max_hcltv": 0.75},
                "rate_term_refi": {"max_ltv": 0.70, "max_cltv": 0.70, "max_hcltv": 0.75},
                "cash_out_refi": {"max_ltv": 0.70, "max_cltv": 0.70, "max_hcltv": 0.75}
            },
            "3_4_unit": {
                "purchase": {"max_ltv": 0.75, "max_cltv": 0.75, "max_hcltv": 0.75},
                "rate_term_refi": {"max_ltv": 0.70, "max_cltv": 0.70, "max_hcltv": 0.75},
                "cash_out_refi": {"max_ltv": 0.70, "max_cltv": 0.70, "max_hcltv": 0.75}
            }
        }
    },

    # Rule 2: Credit Score Minimums
    "credit_score_min": {
        "base": 620,
        "arm": 640,
        "high_balance": 680,
        "2_4_unit": 680,
        "investment": 680,
        "cash_out": 620,
        "7_plus_properties": 720
    },

    # Rule 3: DTI Limits
    "dti_limits": {
        "max_dti_du": 0.50,
        "max_dti_manual_base": 0.36,
        "max_dti_manual_compensating": 0.45
    },

    # Rule 4: Property Type Constraints
    "property_type_rules": {
        "allowed_types": ["SFR", "Condo", "Coop", "Manufactured", "PUD"],
        "coop_no_investment": True,
        "manufactured_max_ltv": 0.95,
        "manufactured_du_only": True
    },

    # Rule 7: Loan Amount Limits (2024 approximation)
    "loan_limits": {
        "baseline": {
            "1_unit": 766550,
            "2_unit": 981500,
            "3_unit": 1186350,
            "4_unit": 1474400
        },
        "high_cost": {
            "1_unit": 1149825,
            "2_unit": 1472250,
            "3_unit": 1779525,
            "4_unit": 2211600
        }
    },

    # Rule 8: MI Coverage Requirements
    "mi_coverage": {
        # LTV range -> coverage percent
        (0.8001, 0.85): 0.12,
        (0.8501, 0.90): 0.25,
        (0.9001, 0.95): 0.30,
        (0.9501, 0.97): 0.35
    },

    # Rule 9: Reserve Requirements
    "reserve_rules": {
        "primary_1_unit": 0,  # months of PITIA
        "primary_2_4_unit": 6,
        "second_home": 2,
        "investment": 6,
        "additional_property_pct": {
            "1_to_4_properties": 0.02,  # 2% of total UPB of other properties
            "5_to_6_properties": 0.04,
            "7_plus_properties": 0.06
        }
    },

    # Rule 10: Financed Properties
    "financed_property_rules": {
        "max_allowed": 10,
        "standard_max": 6,
        "extended_min_credit": 720,
        "extended_du_only": True
    },

    # Rule 12: Property Condition
    "property_condition_rules": {
        "unacceptable_ratings": ["C5", "C6"],
        "acceptable_ratings": ["C1", "C2", "C3", "C4"]
    },

    # Rule 14: First-Time Homebuyer
    "fthb_rules": {
        "max_ltv_non_fthb": 0.95,
        "education_required_ltv": 0.95,
        "ami_waiver_threshold": 1.0,  # 100% of AMI
        "ami_waiver_high_cost_threshold": 1.2  # 120% of AMI
    },

    # Rule 15: HPML/HOEPA Thresholds
    "hpml_hoepa": {
        "hpml_margin_first_lien": 0.015,  # 1.5%
        "hoepa_margin": 0.065,  # 6.5%
        "hoepa_points_fees_threshold": 0.05,  # 5%
        "apor_proxy": 0.055  # simplified APOR proxy
    },

    # Rule 16: LLPA Matrices (simplified for demonstration)
    "llpa": {
        # Base grid: credit score band x LTV bucket
        "base_grid": {
            # Format: (credit_min, credit_max, ltv_min, ltv_max): bps
            (760, 850, 0.0001, 0.6000): 0.00,
            (760, 850, 0.6001, 0.7000): 0.25,
            (760, 850, 0.7001, 0.7500): 0.50,
            (760, 850, 0.7501, 0.8000): 0.75,
            (760, 850, 0.8001, 0.8500): 1.00,
            (760, 850, 0.8501, 0.9000): 1.25,
            (760, 850, 0.9001, 0.9500): 1.50,
            (760, 850, 0.9501, 0.9700): 1.75,

            (740, 759, 0.0001, 0.6000): 0.25,
            (740, 759, 0.6001, 0.7000): 0.50,
            (740, 759, 0.7001, 0.7500): 0.75,
            (740, 759, 0.7501, 0.8000): 1.00,
            (740, 759, 0.8001, 0.8500): 1.50,
            (740, 759, 0.8501, 0.9000): 1.75,
            (740, 759, 0.9001, 0.9500): 2.25,
            (740, 759, 0.9501, 0.9700): 2.75,

            (720, 739, 0.0001, 0.6000): 0.50,
            (720, 739, 0.6001, 0.7000): 0.75,
            (720, 739, 0.7001, 0.7500): 1.25,
            (720, 739, 0.7501, 0.8000): 1.50,
            (720, 739, 0.8001, 0.8500): 2.25,
            (720, 739, 0.8501, 0.9000): 2.75,
            (720, 739, 0.9001, 0.9500): 3.25,
            (720, 739, 0.9501, 0.9700): 3.75,

            (700, 719, 0.0001, 0.6000): 1.00,
            (700, 719, 0.6001, 0.7000): 1.50,
            (700, 719, 0.7001, 0.7500): 2.00,
            (700, 719, 0.7501, 0.8000): 2.50,
            (700, 719, 0.8001, 0.8500): 3.00,
            (700, 719, 0.8501, 0.9000): 3.50,
            (700, 719, 0.9001, 0.9500): 4.25,
            (700, 719, 0.9501, 0.9700): 4.75,

            (680, 699, 0.0001, 0.6000): 1.50,
            (680, 699, 0.6001, 0.7000): 2.00,
            (680, 699, 0.7001, 0.7500): 2.75,
            (680, 699, 0.7501, 0.8000): 3.25,
            (680, 699, 0.8001, 0.8500): 3.75,
            (680, 699, 0.8501, 0.9000): 4.25,
            (680, 699, 0.9001, 0.9500): 5.00,
            (680, 699, 0.9501, 0.9700): 5.50,

            (660, 679, 0.0001, 0.6000): 2.00,
            (660, 679, 0.6001, 0.7000): 2.50,
            (660, 679, 0.7001, 0.7500): 3.25,
            (660, 679, 0.7501, 0.8000): 4.00,
            (660, 679, 0.8001, 0.8500): 4.75,
            (660, 679, 0.8501, 0.9000): 5.25,
            (660, 679, 0.9001, 0.9500): 6.00,
            (660, 679, 0.9501, 0.9700): 6.50,

            (640, 659, 0.0001, 0.6000): 2.50,
            (640, 659, 0.6001, 0.7000): 3.00,
            (640, 659, 0.7001, 0.7500): 3.75,
            (640, 659, 0.7501, 0.8000): 4.50,
            (640, 659, 0.8001, 0.8500): 5.50,
            (640, 659, 0.8501, 0.9000): 6.00,
            (640, 659, 0.9001, 0.9500): 7.00,
            (640, 659, 0.9501, 0.9700): 7.50,

            (620, 639, 0.0001, 0.6000): 3.00,
            (620, 639, 0.6001, 0.7000): 3.50,
            (620, 639, 0.7001, 0.7500): 4.50,
            (620, 639, 0.7501, 0.8000): 5.25,
            (620, 639, 0.8001, 0.8500): 6.25,
            (620, 639, 0.8501, 0.9000): 7.00,
            (620, 639, 0.9001, 0.9500): 8.00,
            (620, 639, 0.9501, 0.9700): 8.50,
        },

        # Adjustment for occupancy
        "adjust_occupancy": {
            "primary": 0.00,
            "second_home": 2.00,
            "investment": 2.75
        },

        # Adjustment for property type
        "adjust_property_type": {
            "SFR": 0.00,
            "PUD": 0.00,
            "Condo": 0.75,
            "Coop": 1.00,
            "Manufactured": 1.50
        },

        # Adjustment for high-balance
        "adjust_high_balance": 0.25,

        # Adjustment for 2-4 units
        "adjust_units": {
            1: 0.00,
            2: 0.50,
            3: 0.75,
            4: 0.75
        },

        # Adjustment for minimum MI coverage
        "adjust_min_mi": 0.75,

        # Adjustment for cash-out
        "adjust_cash_out": 1.25,

        # FTHB waiver (if AMI <= threshold, waive standard LLPAs)
        "waiver_fthb_ami": {
            "enabled": True,
            "waives_base_grid": True,
            "waives_occupancy": True
        },

        # Homeownership counseling credit
        "credit_counseling": 0.125
    },

    # Base rate sheet (simplified)
    "rate_sheet": {
        "standard": {
            (6.00, "fixed_30"): 100.00,  # par pricing at 780+ FICO, ≤60% LTV
            (6.25, "fixed_30"): 100.50,
            (6.50, "fixed_30"): 101.00,
            (6.75, "fixed_30"): 101.50,
            (7.00, "fixed_30"): 102.00
        }
    }
}


# ============================================================================
# RULE IMPLEMENTATIONS
# ============================================================================

def rule_ltv_cltv_hcltv(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 1: LTV / CLTV / HCLTV

    Computes loan-to-value ratios and validates against limits based on:
    - Occupancy type
    - Property units
    - Loan purpose
    """
    prop = scenario.property
    loan = scenario.loan

    # Determine valuation base
    if loan.purpose == "purchase" and prop.purchase_price is not None:
        value = min(prop.purchase_price, prop.appraised_value)
    else:
        value = prop.appraised_value

    # Calculate LTV
    ltv = loan.loan_amount / value if value > 0 else 0.0

    # Calculate CLTV (includes subordinate liens)
    subordinate_balance = sum(
        lien.get("current_balance", 0.0)
        for lien in scenario.financing.subordinate_liens
    )
    cltv = (loan.loan_amount + subordinate_balance) / value if value > 0 else 0.0

    # Calculate HCLTV (includes HELOC credit limits)
    heloc_limits = sum(
        lien.get("credit_limit", lien.get("current_balance", 0.0))
        for lien in scenario.financing.subordinate_liens
        if lien.get("type") == "heloc"
    )
    hcltv = (loan.loan_amount + heloc_limits) / value if value > 0 else 0.0

    # Round up to nearest whole percent (truncate to 2 decimals first)
    ltv = math.ceil(ltv * 10000) / 10000
    cltv = math.ceil(cltv * 10000) / 10000
    hcltv = math.ceil(hcltv * 10000) / 10000

    # Store in context
    context["LTV"] = ltv
    context["CLTV"] = cltv
    context["HCLTV"] = hcltv
    context["value"] = value

    # Determine unit key
    if prop.units == 1:
        unit_key = "1_unit"
    elif prop.units == 2:
        unit_key = "2_unit"
    else:
        unit_key = "3_4_unit"

    # Get limits
    limits = config["ltv_limits"].get(prop.occupancy, {}).get(unit_key, {}).get(loan.purpose, {})

    if not limits:
        return RuleResult(
            rule_name="LTV_CLTV_HCLTV",
            eligible=False,
            messages=[f"No LTV limits defined for {prop.occupancy}/{unit_key}/{loan.purpose}"],
            metrics={"LTV": ltv, "CLTV": cltv, "HCLTV": hcltv}
        )

    max_ltv = limits.get("max_ltv", 0.80)
    max_cltv = limits.get("max_cltv", 0.80)
    max_hcltv = limits.get("max_hcltv", 0.90)

    # Validate
    messages = []
    eligible = True

    if ltv > max_ltv:
        eligible = False
        messages.append(f"LTV {ltv:.2%} exceeds max {max_ltv:.2%}")

    if cltv > max_cltv:
        eligible = False
        messages.append(f"CLTV {cltv:.2%} exceeds max {max_cltv:.2%}")

    if hcltv > max_hcltv:
        eligible = False
        messages.append(f"HCLTV {hcltv:.2%} exceeds max {max_hcltv:.2%}")

    return RuleResult(
        rule_name="LTV_CLTV_HCLTV",
        eligible=eligible,
        messages=messages if messages else ["LTV/CLTV/HCLTV within limits"],
        metrics={
            "LTV": ltv,
            "CLTV": cltv,
            "HCLTV": hcltv,
            "max_ltv": max_ltv,
            "max_cltv": max_cltv,
            "max_hcltv": max_hcltv,
            "value": value
        }
    )


def rule_credit_score(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 2: Credit Score (FICO)

    Validates minimum credit score requirements based on:
    - Loan type (ARM vs Fixed)
    - Channel (conforming vs high-balance)
    - Property units
    - Occupancy
    - Number of financed properties
    """
    credit = scenario.borrower.credit_score
    mins = config["credit_score_min"]

    # Determine minimum
    min_required = mins["base"]

    if scenario.loan.arm:
        min_required = max(min_required, mins["arm"])

    if scenario.loan.channel == "high_balance":
        min_required = max(min_required, mins["high_balance"])

    if scenario.property.units >= 2:
        min_required = max(min_required, mins["2_4_unit"])

    if scenario.property.occupancy == "investment":
        min_required = max(min_required, mins["investment"])

    if scenario.loan.purpose == "cash_out_refi":
        min_required = max(min_required, mins["cash_out"])

    if scenario.borrower.num_financed_properties >= 7:
        min_required = max(min_required, mins["7_plus_properties"])

    context["min_credit_score"] = min_required

    eligible = credit >= min_required
    messages = []

    if not eligible:
        messages.append(f"Credit score {credit} below minimum {min_required}")
    else:
        messages.append(f"Credit score {credit} meets minimum {min_required}")

    return RuleResult(
        rule_name="CREDIT_SCORE",
        eligible=eligible,
        messages=messages,
        metrics={"credit_score": credit, "min_required": min_required}
    )


def rule_dti(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 3: Debt-to-Income Ratio (DTI)

    Calculates DTI and validates against DU and manual underwriting thresholds.
    """
    borrower = scenario.borrower
    loan = scenario.loan

    # Calculate monthly PITIA (simplified)
    # P&I approximation using standard mortgage formula
    monthly_rate = loan.note_rate / 12.0 / 100.0
    num_payments = loan.term_months

    if monthly_rate > 0:
        monthly_pi = loan.loan_amount * (
            monthly_rate * (1 + monthly_rate) ** num_payments
        ) / ((1 + monthly_rate) ** num_payments - 1)
    else:
        monthly_pi = loan.loan_amount / num_payments

    # Estimate taxes, insurance, HOA (simplified: 0.5% of value annually)
    estimated_tia = context.get("value", loan.loan_amount) * 0.005 / 12

    # MI payment (if applicable)
    mi_payment = 0.0
    if scenario.financing.mi_type and scenario.financing.mi_coverage_pct:
        # Approximate MI rate: 0.5% annual for 25% coverage
        mi_annual_rate = scenario.financing.mi_coverage_pct * 0.02
        mi_payment = loan.loan_amount * mi_annual_rate / 12

    monthly_pitia = monthly_pi + estimated_tia + mi_payment

    # Total debts
    total_debts = monthly_pitia + sum(borrower.monthly_debts.values())

    # DTI and FEDTI
    dti = total_debts / borrower.gross_monthly_income if borrower.gross_monthly_income > 0 else 999.0
    fedti = monthly_pitia / borrower.gross_monthly_income if borrower.gross_monthly_income > 0 else 999.0

    context["DTI"] = dti
    context["FEDTI"] = fedti
    context["monthly_pitia"] = monthly_pitia

    # Check limits
    limits = config["dti_limits"]
    max_dti_du = limits["max_dti_du"]
    max_dti_manual_base = limits["max_dti_manual_base"]
    max_dti_manual_comp = limits["max_dti_manual_compensating"]

    eligible = dti <= max_dti_du
    messages = []

    if dti > max_dti_du:
        eligible = False
        messages.append(f"DTI {dti:.2%} exceeds DU max {max_dti_du:.2%}")
    elif dti > max_dti_manual_comp:
        messages.append(f"DTI {dti:.2%} requires DU approval (exceeds manual {max_dti_manual_comp:.2%})")
        context["requires_du"] = True
    elif dti > max_dti_manual_base:
        messages.append(f"DTI {dti:.2%} requires compensating factors or DU")
    else:
        messages.append(f"DTI {dti:.2%} within standard limits")

    return RuleResult(
        rule_name="DTI",
        eligible=eligible,
        messages=messages,
        metrics={
            "DTI": dti,
            "monthly_pitia": monthly_pitia,
            "total_debts": total_debts,
            "max_dti_du": max_dti_du
        }
    )


def rule_property_type(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 4: Property Type

    Validates property type and enforces type-specific constraints.
    """
    prop = scenario.property
    rules = config["property_type_rules"]

    allowed = rules["allowed_types"]

    if prop.property_type not in allowed:
        return RuleResult(
            rule_name="PROPERTY_TYPE",
            eligible=False,
            messages=[f"Property type {prop.property_type} not allowed"],
            metrics={"property_type": prop.property_type}
        )

    messages = []
    eligible = True

    # Co-op investment restriction
    if prop.property_type == "Coop" and prop.occupancy == "investment":
        if rules["coop_no_investment"]:
            eligible = False
            messages.append("Co-op investment properties not allowed")

    # Manufactured constraints
    if prop.property_type == "Manufactured":
        max_ltv_manufactured = rules.get("manufactured_max_ltv", 0.95)
        current_ltv = context.get("LTV", 0.0)

        if current_ltv > max_ltv_manufactured:
            eligible = False
            messages.append(f"Manufactured home LTV {current_ltv:.2%} exceeds max {max_ltv_manufactured:.2%}")

        if rules.get("manufactured_du_only"):
            context["requires_du"] = True
            messages.append("Manufactured home requires DU approval")

    # Unit validation
    if prop.units < 1 or prop.units > 4:
        eligible = False
        messages.append(f"Property must be 1-4 units, got {prop.units}")

    if not messages:
        messages.append(f"Property type {prop.property_type} acceptable")

    return RuleResult(
        rule_name="PROPERTY_TYPE",
        eligible=eligible,
        messages=messages,
        metrics={"property_type": prop.property_type, "units": prop.units}
    )


def rule_occupancy(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 5: Occupancy Type

    Validates occupancy and enforces occupancy-specific rules.
    """
    prop = scenario.property

    allowed_occupancy = ["primary", "second_home", "investment"]

    if prop.occupancy not in allowed_occupancy:
        return RuleResult(
            rule_name="OCCUPANCY",
            eligible=False,
            messages=[f"Invalid occupancy type: {prop.occupancy}"],
            metrics={"occupancy": prop.occupancy}
        )

    messages = []
    eligible = True

    # Second home must be 1-unit
    if prop.occupancy == "second_home" and prop.units != 1:
        eligible = False
        messages.append("Second homes must be 1-unit properties")

    # Set flags
    if prop.occupancy == "investment":
        context["is_investor_loan"] = True

    if not messages:
        messages.append(f"Occupancy {prop.occupancy} acceptable")

    return RuleResult(
        rule_name="OCCUPANCY",
        eligible=eligible,
        messages=messages,
        metrics={"occupancy": prop.occupancy}
    )


def rule_loan_purpose(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 6: Loan Purpose

    Validates loan purpose and determines cash-out classification.
    """
    loan = scenario.loan

    allowed_purposes = ["purchase", "rate_term_refi", "cash_out_refi"]

    if loan.purpose not in allowed_purposes:
        return RuleResult(
            rule_name="LOAN_PURPOSE",
            eligible=False,
            messages=[f"Invalid loan purpose: {loan.purpose}"],
            metrics={"purpose": loan.purpose}
        )

    messages = []

    # Determine if true cash-out
    is_cash_out = loan.purpose == "cash_out_refi"
    context["is_cash_out"] = is_cash_out

    if is_cash_out:
        messages.append("Cash-out refinance: stricter LTV limits apply")
    else:
        messages.append(f"Purpose: {loan.purpose}")

    return RuleResult(
        rule_name="LOAN_PURPOSE",
        eligible=True,
        messages=messages,
        metrics={"purpose": loan.purpose, "is_cash_out": is_cash_out}
    )


def rule_loan_amount_limits(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 7: Loan Amount Limits

    Determines conforming vs high-balance vs jumbo classification.
    """
    loan = scenario.loan
    prop = scenario.property
    limits_config = config["loan_limits"]

    # Determine unit key
    unit_key = f"{prop.units}_unit"

    # Get baseline limit
    baseline_limit = limits_config["baseline"].get(unit_key, 766550)

    # Get high-cost limit if applicable
    if prop.is_high_cost_area:
        max_limit = limits_config["high_cost"].get(unit_key, baseline_limit * 1.5)
        channel = "high_balance" if loan.loan_amount > baseline_limit else "conforming"
    else:
        max_limit = baseline_limit
        channel = "conforming"

    # Check if jumbo
    if loan.loan_amount > max_limit:
        return RuleResult(
            rule_name="LOAN_AMOUNT_LIMITS",
            eligible=False,
            messages=[f"Loan amount ${loan.loan_amount:,.0f} exceeds {channel} limit ${max_limit:,.0f} (jumbo)"],
            metrics={
                "loan_amount": loan.loan_amount,
                "max_limit": max_limit,
                "channel": "jumbo"
            }
        )

    context["channel"] = channel
    context["loan_limit"] = max_limit

    return RuleResult(
        rule_name="LOAN_AMOUNT_LIMITS",
        eligible=True,
        messages=[f"Loan amount ${loan.loan_amount:,.0f} within {channel} limits (max ${max_limit:,.0f})"],
        metrics={
            "loan_amount": loan.loan_amount,
            "max_limit": max_limit,
            "channel": channel
        }
    )


def rule_mortgage_insurance(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 8: Mortgage Insurance Requirements

    Determines MI requirements when LTV > 80% and validates coverage.
    """
    ltv = context.get("LTV", 0.0)

    if ltv <= 0.80:
        return RuleResult(
            rule_name="MORTGAGE_INSURANCE",
            eligible=True,
            messages=["No MI required (LTV ≤ 80%)"],
            metrics={"mi_required": False, "LTV": ltv}
        )

    # MI is required
    mi_coverage_table = config["mi_coverage"]

    # Find required coverage
    required_coverage = 0.0
    for (ltv_min, ltv_max), coverage in mi_coverage_table.items():
        if ltv_min < ltv <= ltv_max:
            required_coverage = coverage
            break

    # Check if MI is provided
    provided_mi = scenario.financing.mi_type is not None
    provided_coverage = scenario.financing.mi_coverage_pct or 0.0

    context["mi_required"] = True
    context["mi_coverage_required"] = required_coverage
    context["mi_coverage_provided"] = provided_coverage

    messages = []
    eligible = True

    if not provided_mi:
        eligible = False
        messages.append(f"MI required for LTV {ltv:.2%} (min {required_coverage:.0%} coverage)")
    elif provided_coverage < required_coverage:
        # Minimum MI allowed but will trigger LLPA
        context["mi_below_standard"] = True
        messages.append(f"MI coverage {provided_coverage:.0%} below standard {required_coverage:.0%} (LLPA applies)")
    else:
        messages.append(f"MI {provided_coverage:.0%} coverage meets requirement")

    return RuleResult(
        rule_name="MORTGAGE_INSURANCE",
        eligible=eligible,
        messages=messages,
        metrics={
            "mi_required": True,
            "required_coverage": required_coverage,
            "provided_coverage": provided_coverage,
            "LTV": ltv
        }
    )


def rule_reserves(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 9: Reserve Requirements

    Calculates required liquid reserves based on occupancy, units, and number of properties.
    """
    borrower = scenario.borrower
    prop = scenario.property
    reserve_rules = config["reserve_rules"]

    monthly_pitia = context.get("monthly_pitia", 0.0)

    # Base reserves in months
    if prop.occupancy == "primary":
        if prop.units == 1:
            base_months = reserve_rules["primary_1_unit"]
        else:
            base_months = reserve_rules["primary_2_4_unit"]
    elif prop.occupancy == "second_home":
        base_months = reserve_rules["second_home"]
    else:  # investment
        base_months = reserve_rules["investment"]

    # Additional reserves for multiple properties
    num_props = borrower.num_financed_properties
    additional_pct_rules = reserve_rules["additional_property_pct"]

    if num_props >= 7:
        additional_pct = additional_pct_rules["7_plus_properties"]
    elif num_props >= 5:
        additional_pct = additional_pct_rules["5_to_6_properties"]
    elif num_props >= 2:
        additional_pct = additional_pct_rules["1_to_4_properties"]
    else:
        additional_pct = 0.0

    # Estimate total UPB of other properties (simplified: assume $300k avg per property)
    other_properties_upb = (num_props - 1) * 300000 if num_props > 1 else 0
    additional_reserves = other_properties_upb * additional_pct

    # Total required reserves
    base_reserves = base_months * monthly_pitia
    total_required = base_reserves + additional_reserves

    # Compare to available
    available = borrower.liquid_assets_after_closing

    context["reserves_required_dollars"] = total_required
    context["reserves_required_months"] = base_months
    context["reserves_available"] = available

    eligible = available >= total_required
    messages = []

    if not eligible:
        shortage = total_required - available
        messages.append(
            f"Insufficient reserves: ${available:,.0f} available vs ${total_required:,.0f} required "
            f"({base_months} months PITIA + ${additional_reserves:,.0f} for {num_props} properties), "
            f"shortage ${shortage:,.0f}"
        )
    else:
        messages.append(
            f"Sufficient reserves: ${available:,.0f} available vs ${total_required:,.0f} required "
            f"({base_months} months + additional for {num_props} properties)"
        )

    return RuleResult(
        rule_name="RESERVES",
        eligible=eligible,
        messages=messages,
        metrics={
            "required_dollars": total_required,
            "required_months": base_months,
            "available_dollars": available
        }
    )


def rule_financed_properties(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 10: Number of Financed Properties

    Validates the number of financed properties and enforces extended portfolio rules.
    """
    num_props = scenario.borrower.num_financed_properties
    rules = config["financed_property_rules"]

    max_allowed = rules["max_allowed"]
    standard_max = rules["standard_max"]

    if num_props > max_allowed:
        return RuleResult(
            rule_name="FINANCED_PROPERTIES",
            eligible=False,
            messages=[f"Too many financed properties: {num_props} (max {max_allowed})"],
            metrics={"num_financed_properties": num_props}
        )

    messages = []

    if num_props > standard_max:
        # Extended portfolio (7-10)
        min_credit = rules["extended_min_credit"]

        if scenario.borrower.credit_score < min_credit:
            return RuleResult(
                rule_name="FINANCED_PROPERTIES",
                eligible=False,
                messages=[
                    f"{num_props} financed properties requires min credit score {min_credit}, "
                    f"got {scenario.borrower.credit_score}"
                ],
                metrics={"num_financed_properties": num_props}
            )

        if rules["extended_du_only"]:
            context["requires_du"] = True
            messages.append(f"{num_props} financed properties requires DU approval")

        messages.append(f"Extended portfolio: {num_props} properties (7-10 range)")
    else:
        messages.append(f"Standard portfolio: {num_props} properties")

    return RuleResult(
        rule_name="FINANCED_PROPERTIES",
        eligible=True,
        messages=messages,
        metrics={"num_financed_properties": num_props}
    )


def rule_income_documentation(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 11: Income Documentation Type

    Enforces full documentation requirement for conforming loans.
    """
    doc_type = scenario.borrower.doc_type

    if doc_type != "full":
        return RuleResult(
            rule_name="INCOME_DOCUMENTATION",
            eligible=False,
            messages=[f"Only full documentation allowed for conforming loans, got '{doc_type}'"],
            metrics={"doc_type": doc_type}
        )

    return RuleResult(
        rule_name="INCOME_DOCUMENTATION",
        eligible=True,
        messages=["Full documentation provided"],
        metrics={"doc_type": doc_type}
    )


def rule_property_condition(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 12: Property Condition & Appraisal Acceptability

    Validates property condition rating from appraisal.
    """
    condition = scenario.property.condition_rating
    rules = config["property_condition_rules"]

    unacceptable = rules["unacceptable_ratings"]

    if condition in unacceptable:
        return RuleResult(
            rule_name="PROPERTY_CONDITION",
            eligible=False,
            messages=[f"Property condition {condition} unacceptable - requires repair to C4 or better"],
            metrics={"condition_rating": condition}
        )

    return RuleResult(
        rule_name="PROPERTY_CONDITION",
        eligible=True,
        messages=[f"Property condition {condition} acceptable"],
        metrics={"condition_rating": condition}
    )


def rule_aus_manual_uw(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 13: AUS vs Manual Underwriting Thresholds

    Determines if loan requires DU approval or is eligible for manual underwriting.
    """
    requires_du = context.get("requires_du", False)
    dti = context.get("DTI", 0.0)

    limits = config["dti_limits"]
    max_manual_comp = limits["max_dti_manual_compensating"]

    manual_eligible = dti <= max_manual_comp and not requires_du

    context["manual_uw_eligible"] = manual_eligible

    messages = []

    if requires_du:
        messages.append("DU approval required (extended portfolio, high DTI, or manufactured home)")
    elif manual_eligible:
        messages.append("Eligible for manual underwriting")
    else:
        messages.append("Loan characteristics suggest DU path preferred")

    return RuleResult(
        rule_name="AUS_MANUAL_UW",
        eligible=True,  # This rule doesn't fail, just classifies
        messages=messages,
        metrics={
            "requires_du": requires_du,
            "manual_eligible": manual_eligible
        }
    )


def rule_first_time_homebuyer(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 14: First-Time Homebuyer (FTHB)

    Validates FTHB status for high-LTV loans and determines LLPA waiver eligibility.
    """
    borrower = scenario.borrower
    prop = scenario.property
    ltv = context.get("LTV", 0.0)

    rules = config["fthb_rules"]

    # Determine FTHB status
    is_fthb = borrower.first_time_homebuyer or not borrower.owns_property_last_3yrs
    context["is_fthb"] = is_fthb

    messages = []
    eligible = True

    # High-LTV requirement
    max_ltv_non_fthb = rules["max_ltv_non_fthb"]

    if ltv > max_ltv_non_fthb and not is_fthb:
        eligible = False
        messages.append(f"LTV {ltv:.2%} > {max_ltv_non_fthb:.2%} requires first-time homebuyer status")

    # Education requirement
    education_ltv = rules["education_required_ltv"]
    if is_fthb and ltv > education_ltv:
        context["homeownership_education_required"] = True
        messages.append(f"Homeownership education required for FTHB with LTV > {education_ltv:.2%}")

    # LLPA waiver eligibility
    ami_ratio = borrower.ami_ratio or 999.0
    ami_threshold = rules["ami_waiver_threshold"]

    if prop.is_high_cost_area:
        ami_threshold = rules["ami_waiver_high_cost_threshold"]

    if is_fthb and ami_ratio <= ami_threshold:
        context["fthb_llpa_waiver_eligible"] = True
        messages.append(f"Eligible for FTHB LLPA waiver (AMI ratio {ami_ratio:.1%} ≤ {ami_threshold:.0%})")

    if not messages:
        messages.append(f"FTHB status: {is_fthb}")

    return RuleResult(
        rule_name="FIRST_TIME_HOMEBUYER",
        eligible=eligible,
        messages=messages,
        metrics={
            "is_fthb": is_fthb,
            "ami_ratio": ami_ratio,
            "llpa_waiver_eligible": context.get("fthb_llpa_waiver_eligible", False)
        }
    )


def rule_high_cost_hpml_hcltv(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 15: High-Cost Area / HPML / HOEPA / HCLTV

    Flags HPML and HOEPA status; HOEPA loans are ineligible.
    """
    loan = scenario.loan
    thresholds = config["hpml_hoepa"]

    # Simplified APR calculation
    # APR ≈ note_rate + (points_and_fees / loan_amount / term_years)
    # Assume 1% origination + LLPA as points
    estimated_points = 1.0  # Will refine after LLPA calculation
    points_and_fees_pct = estimated_points / 100.0

    term_years = loan.term_months / 12.0
    apr = loan.note_rate + (points_and_fees_pct * 100.0 / term_years)

    apor = thresholds["apor_proxy"]

    # HPML check
    hpml_margin = thresholds["hpml_margin_first_lien"]
    is_hpml = (apr / 100.0) >= (apor + hpml_margin)

    # HOEPA check
    hoepa_margin = thresholds["hoepa_margin"]
    hoepa_points_threshold = thresholds["hoepa_points_fees_threshold"]

    is_hoepa = (
        (apr / 100.0) >= (apor + hoepa_margin) or
        points_and_fees_pct >= hoepa_points_threshold
    )

    context["is_hpml"] = is_hpml
    context["is_hoepa"] = is_hoepa
    context["apr"] = apr

    messages = []
    eligible = True

    if is_hoepa:
        eligible = False
        messages.append(f"HOEPA violation: APR {apr:.3f}% or points {points_and_fees_pct:.2%} exceeds HOEPA thresholds")
    elif is_hpml:
        messages.append(f"HPML flagged: APR {apr:.3f}% ≥ APOR {apor:.3%} + {hpml_margin:.3%} (ensure HPML requirements met)")
    else:
        messages.append("Not HPML or HOEPA")

    return RuleResult(
        rule_name="HIGH_COST_HPML_HCLTV",
        eligible=eligible,
        messages=messages,
        metrics={
            "is_hpml": is_hpml,
            "is_hoepa": is_hoepa,
            "apr": apr,
            "apor": apor
        }
    )


def rule_llpa(scenario: ScenarioInput, config: Dict, context: Dict) -> RuleResult:
    """
    Rule 16: Loan-Level Price Adjustments (LLPAs)

    Calculates total LLPA based on credit, LTV, occupancy, property type, and other factors.
    Applies waivers for FTHB with low AMI.
    """
    borrower = scenario.borrower
    prop = scenario.property
    loan = scenario.loan

    ltv = context.get("LTV", 0.0)
    credit = borrower.credit_score

    llpa_config = config["llpa"]

    components = []

    # 1. Base grid (credit x LTV)
    base_llpa = 0.0
    base_grid = llpa_config["base_grid"]

    for (credit_min, credit_max, ltv_min, ltv_max), bps in base_grid.items():
        if credit_min <= credit <= credit_max and ltv_min < ltv <= ltv_max:
            base_llpa = bps
            components.append(PricingComponent(
                name="Base_Credit_LTV",
                value_bps=bps,
                reason=f"Credit {credit} in [{credit_min}-{credit_max}], LTV {ltv:.2%} in ({ltv_min:.2%}-{ltv_max:.2%}]"
            ))
            break

    # 2. Occupancy adjustment
    occupancy_adjust = llpa_config["adjust_occupancy"].get(prop.occupancy, 0.0)
    if occupancy_adjust > 0:
        components.append(PricingComponent(
            name="Occupancy_Adjustment",
            value_bps=occupancy_adjust,
            reason=f"{prop.occupancy} occupancy"
        ))

    # 3. Property type adjustment
    property_adjust = llpa_config["adjust_property_type"].get(prop.property_type, 0.0)
    if property_adjust > 0:
        components.append(PricingComponent(
            name="Property_Type_Adjustment",
            value_bps=property_adjust,
            reason=f"{prop.property_type} property type"
        ))

    # 4. High-balance adjustment
    channel = context.get("channel", "conforming")
    if channel == "high_balance":
        hb_adjust = llpa_config["adjust_high_balance"]
        components.append(PricingComponent(
            name="High_Balance_Adjustment",
            value_bps=hb_adjust,
            reason="High-balance loan"
        ))

    # 5. Units adjustment
    units_adjust = llpa_config["adjust_units"].get(prop.units, 0.0)
    if units_adjust > 0:
        components.append(PricingComponent(
            name="Units_Adjustment",
            value_bps=units_adjust,
            reason=f"{prop.units}-unit property"
        ))

    # 6. Minimum MI adjustment
    if context.get("mi_below_standard", False):
        mi_adjust = llpa_config["adjust_min_mi"]
        components.append(PricingComponent(
            name="Minimum_MI_Adjustment",
            value_bps=mi_adjust,
            reason="MI coverage below standard"
        ))

    # 7. Cash-out adjustment
    if context.get("is_cash_out", False):
        co_adjust = llpa_config["adjust_cash_out"]
        components.append(PricingComponent(
            name="Cash_Out_Adjustment",
            value_bps=co_adjust,
            reason="Cash-out refinance"
        ))

    # Sum all components
    total_llpa = sum(c.value_bps for c in components)

    # 8. Apply waivers
    waivers = []

    if context.get("fthb_llpa_waiver_eligible", False):
        waiver_config = llpa_config["waiver_fthb_ami"]

        if waiver_config["enabled"]:
            waived_amount = 0.0

            # Waive base grid
            if waiver_config["waives_base_grid"]:
                waived_amount += base_llpa

            # Waive occupancy
            if waiver_config["waives_occupancy"]:
                waived_amount += occupancy_adjust

            if waived_amount > 0:
                total_llpa -= waived_amount
                waivers.append(f"FTHB_AMI_Waiver: -{waived_amount:.2f} bps")
                components.append(PricingComponent(
                    name="FTHB_AMI_Waiver",
                    value_bps=-waived_amount,
                    reason="First-time homebuyer with income ≤ AMI threshold"
                ))

    # Homeownership counseling credit
    if context.get("homeownership_education_required", False):
        counseling_credit = llpa_config["credit_counseling"]
        total_llpa -= counseling_credit
        waivers.append(f"Homeownership_Counseling_Credit: -{counseling_credit:.2f} bps")
        components.append(PricingComponent(
            name="Counseling_Credit",
            value_bps=-counseling_credit,
            reason="Homeownership counseling completed"
        ))

    context["llpa_total_bps"] = total_llpa
    context["llpa_components"] = components
    context["llpa_waivers"] = waivers

    return RuleResult(
        rule_name="LLPA",
        eligible=True,  # LLPA doesn't fail eligibility
        messages=[f"Total LLPA: {total_llpa:.2f} bps ({len(components)} components, {len(waivers)} waivers)"],
        metrics={
            "total_llpa_bps": total_llpa,
            "num_components": len(components),
            "num_waivers": len(waivers)
        }
    )


# ============================================================================
# PRICING ENGINE
# ============================================================================

def get_base_price(note_rate: float, product_key: str, config: Dict) -> float:
    """
    Retrieve base price from rate sheet for given note rate and product.

    Uses linear interpolation if exact rate not found.
    """
    rate_sheet_id = "standard"
    rate_sheet = config["rate_sheet"].get(rate_sheet_id, {})

    # Find exact match or interpolate
    product_rates = {rate: price for (rate, prod), price in rate_sheet.items() if prod == product_key}

    if not product_rates:
        return 100.0  # Default par

    if note_rate in product_rates:
        return product_rates[note_rate]

    # Linear interpolation
    rates_sorted = sorted(product_rates.keys())

    if note_rate < rates_sorted[0]:
        return product_rates[rates_sorted[0]]

    if note_rate > rates_sorted[-1]:
        return product_rates[rates_sorted[-1]]

    # Find bracketing rates
    for i in range(len(rates_sorted) - 1):
        r1, r2 = rates_sorted[i], rates_sorted[i + 1]
        if r1 <= note_rate <= r2:
            p1, p2 = product_rates[r1], product_rates[r2]
            # Linear interpolation
            weight = (note_rate - r1) / (r2 - r1)
            return p1 + weight * (p2 - p1)

    return 100.0


def compute_pricing(scenario: ScenarioInput, context: Dict, config: Dict) -> PricingResult:
    """
    Compute final pricing with base rate and LLPA adjustments.
    """
    loan = scenario.loan

    # Determine product key
    product_key = f"{scenario.loan.product_type}_{loan.term_months // 12}"
    if product_key.startswith("fixed"):
        product_key = "fixed_30"  # Simplify to standard 30-year

    # Get base price
    base_price = get_base_price(loan.note_rate, product_key, config)

    # Get LLPA
    llpa_total_bps = context.get("llpa_total_bps", 0.0)
    components = context.get("llpa_components", [])
    waivers = context.get("llpa_waivers", [])

    # Convert LLPA to price adjustment (negative = cost to borrower, lowers price)
    price_adjustment = -llpa_total_bps / 100.0

    # Net price
    net_price = base_price + price_adjustment

    # Notes
    notes = []
    if context.get("is_hpml", False):
        notes.append("HPML: Ensure escrow requirements and additional HPML disclosures are met")

    if context.get("homeownership_education_required", False):
        notes.append("Homeownership education required for borrower")

    return PricingResult(
        base_rate=loan.note_rate,
        base_price=base_price,
        llpa_total_bps=llpa_total_bps,
        components=components,
        waivers_applied=waivers,
        net_price=net_price,
        notes=notes
    )


# ============================================================================
# ENGINE ORCHESTRATION
# ============================================================================

def run_rules(scenario: ScenarioInput, config: Dict) -> Tuple[List[RuleResult], Dict]:
    """
    Execute all 16 eligibility rules in order, accumulating context.

    Returns:
        Tuple of (rule_results, context_dict)
    """
    context: Dict[str, Any] = {}
    results: List[RuleResult] = []

    # Execute rules in dependency order
    rules_to_run = [
        rule_ltv_cltv_hcltv,       # 1
        rule_credit_score,          # 2
        rule_dti,                   # 3
        rule_property_type,         # 4
        rule_occupancy,             # 5
        rule_loan_purpose,          # 6
        rule_loan_amount_limits,    # 7
        rule_mortgage_insurance,    # 8
        rule_reserves,              # 9
        rule_financed_properties,   # 10
        rule_income_documentation,  # 11
        rule_property_condition,    # 12
        rule_aus_manual_uw,         # 13
        rule_first_time_homebuyer,  # 14
        rule_high_cost_hpml_hcltv,  # 15
        rule_llpa,                  # 16
    ]

    for rule_func in rules_to_run:
        result = rule_func(scenario, config, context)
        results.append(result)

    return results, context


def aggregate_eligibility(rule_results: List[RuleResult]) -> bool:
    """
    Determine overall eligibility from all rule results.

    Overall eligible only if ALL mandatory rules pass.
    LLPA rule is informational and doesn't affect eligibility.
    """
    for result in rule_results:
        # LLPA doesn't affect eligibility
        if result.rule_name == "LLPA":
            continue

        if not result.eligible:
            return False

    return True


def price_scenario(
    scenario: ScenarioInput,
    config: Optional[Dict] = None
) -> EngineResult:
    """
    Main entry point: evaluate scenario and produce complete result with eligibility and pricing.

    Args:
        scenario: Complete mortgage scenario input
        config: Optional custom configuration (uses DEFAULT_CONFIG if not provided)

    Returns:
        EngineResult with eligibility, pricing, and detailed rule results
    """
    if config is None:
        config = DEFAULT_CONFIG

    # Run all rules
    rule_results, context = run_rules(scenario, config)

    # Aggregate eligibility
    eligible = aggregate_eligibility(rule_results)

    # Compute pricing (even if ineligible, for diagnostic purposes)
    pricing = compute_pricing(scenario, context, config)

    # Extract calculated metrics
    calculated_metrics = {
        "LTV": context.get("LTV", 0.0),
        "CLTV": context.get("CLTV", 0.0),
        "HCLTV": context.get("HCLTV", 0.0),
        "DTI": context.get("DTI", 0.0),
        "FEDTI": context.get("FEDTI", 0.0),
        "reserves_required_dollars": context.get("reserves_required_dollars", 0.0),
        "reserves_required_months": context.get("reserves_required_months", 0.0),
        "value": context.get("value", 0.0),
        "channel": context.get("channel", "unknown")
    }

    # Extract flags
    flags = {
        "HPML": context.get("is_hpml", False),
        "HOEPA": context.get("is_hoepa", False),
        "ManualUWOnly": not context.get("requires_du", False) and context.get("manual_uw_eligible", False),
        "DU_Required": context.get("requires_du", False),
        "FTHB": context.get("is_fthb", False),
        "InvestorLoan": context.get("is_investor_loan", False),
        "CashOut": context.get("is_cash_out", False),
        "MI_Required": context.get("mi_required", False)
    }

    return EngineResult(
        eligibility_overall=eligible,
        rule_results=rule_results,
        pricing=pricing,
        calculated_metrics=calculated_metrics,
        flags=flags
    )


# ============================================================================
# DEMO / CLI
# ============================================================================

def demo():
    """
    Demonstration of the mortgage engine with three sample scenarios.
    """
    print("=" * 80)
    print("MORTGAGE ELIGIBILITY AND PRICING ENGINE - DEMONSTRATION")
    print("=" * 80)
    print()

    # Scenario A: Prime conforming purchase
    print("SCENARIO A: Prime Conforming Purchase")
    print("-" * 80)

    scenario_a = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=760,
            gross_monthly_income=10000.0,
            monthly_debts={"car": 400.0, "student": 250.0},
            num_financed_properties=1,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=50000.0,
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
            county="Los Angeles",
            is_high_cost_area=True,
            project_type=None
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
        financing=FinancingStructure(
            subordinate_liens=[],
            mi_type=None,
            mi_coverage_pct=None
        )
    )

    result_a = price_scenario(scenario_a)
    print_result_summary(result_a)
    print()

    # Scenario B: High-LTV FTHB
    print("SCENARIO B: High-LTV First-Time Homebuyer (97% LTV)")
    print("-" * 80)

    scenario_b = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=700,
            gross_monthly_income=6000.0,
            monthly_debts={"car": 300.0},
            num_financed_properties=1,
            first_time_homebuyer=True,
            owns_property_last_3yrs=False,
            liquid_assets_after_closing=10000.0,
            doc_type="full",
            ami_ratio=0.85  # 85% of AMI - eligible for LLPA waiver
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
            is_high_cost_area=False,
            project_type=None
        ),
        loan=LoanTerms(
            loan_amount=291000.0,  # 97% LTV
            note_rate=6.75,
            term_months=360,
            arm=False,
            purpose="purchase",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure(
            subordinate_liens=[],
            mi_type="borrower_paid_monthly",
            mi_coverage_pct=0.35  # 35% coverage for 97% LTV
        )
    )

    result_b = price_scenario(scenario_b)
    print_result_summary(result_b)
    print()

    # Scenario C: Investment property cash-out with multiple properties
    print("SCENARIO C: Investment Property Cash-Out Refinance (Multiple Properties)")
    print("-" * 80)

    scenario_c = ScenarioInput(
        borrower=BorrowerProfile(
            credit_score=740,
            gross_monthly_income=15000.0,
            monthly_debts={"auto": 500.0, "other_mortgages": 3000.0},
            num_financed_properties=4,
            first_time_homebuyer=False,
            owns_property_last_3yrs=True,
            liquid_assets_after_closing=100000.0,
            doc_type="full"
        ),
        property=PropertyProfile(
            purchase_price=None,
            appraised_value=500000.0,
            units=1,
            property_type="SFR",
            occupancy="investment",
            condition_rating="C2",
            state="FL",
            county="Miami-Dade",
            is_high_cost_area=False,
            project_type=None
        ),
        loan=LoanTerms(
            loan_amount=375000.0,  # 75% LTV
            note_rate=7.00,
            term_months=360,
            arm=False,
            purpose="cash_out_refi",
            product_type="fixed",
            channel="conforming"
        ),
        financing=FinancingStructure(
            subordinate_liens=[],
            mi_type=None,
            mi_coverage_pct=None
        )
    )

    result_c = price_scenario(scenario_c)
    print_result_summary(result_c)
    print()


def print_result_summary(result: EngineResult) -> None:
    """Print a formatted summary of engine results."""

    # Eligibility
    status = "✓ APPROVED" if result.eligibility_overall else "✗ DENIED"
    print(f"Overall Eligibility: {status}")
    print()

    # Calculated Metrics
    print("Calculated Metrics:")
    metrics = result.calculated_metrics
    print(f"  LTV:      {metrics.get('LTV', 0):.2%}")
    print(f"  CLTV:     {metrics.get('CLTV', 0):.2%}")
    print(f"  HCLTV:    {metrics.get('HCLTV', 0):.2%}")
    print(f"  DTI:      {metrics.get('DTI', 0):.2%}")
    print(f"  Channel:  {metrics.get('channel', 'N/A')}")
    print(f"  Reserves: ${metrics.get('reserves_required_dollars', 0):,.0f} "
          f"({metrics.get('reserves_required_months', 0):.0f} months)")
    print()

    # Flags
    print("Flags:")
    for flag, value in result.flags.items():
        if value:
            print(f"  • {flag}")
    print()

    # Failed Rules
    failed_rules = [r for r in result.rule_results if not r.eligible]
    if failed_rules:
        print("Failed Rules:")
        for rule in failed_rules:
            print(f"  ✗ {rule.rule_name}:")
            for msg in rule.messages:
                print(f"      {msg}")
        print()

    # Pricing
    if result.pricing:
        pricing = result.pricing
        print("Pricing:")
        print(f"  Base Rate:    {pricing.base_rate:.3f}%")
        print(f"  Base Price:   {pricing.base_price:.3f}%")
        print(f"  Total LLPA:   {pricing.llpa_total_bps:.2f} bps")
        print(f"  Net Price:    {pricing.net_price:.3f}%")
        print()

        if pricing.components:
            print("  LLPA Components:")
            for comp in pricing.components:
                sign = "+" if comp.value_bps >= 0 else ""
                print(f"    {comp.name:30s} {sign}{comp.value_bps:6.2f} bps  ({comp.reason})")
            print()

        if pricing.waivers_applied:
            print("  Waivers Applied:")
            for waiver in pricing.waivers_applied:
                print(f"    • {waiver}")
            print()

        if pricing.notes:
            print("  Notes:")
            for note in pricing.notes:
                print(f"    • {note}")
            print()


if __name__ == "__main__":
    # Print README
    print(README_TEXT)
    print("\n" * 2)

    # Run demo
    demo()
