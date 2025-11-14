"""
Community Intelligence Data Models

This module defines all dataclasses for the CommunityInsightEngine,
which identifies underserved communities and generates tailored mortgage recommendations.

Compatible with the existing 16-rule Fannie Mae mortgage pricing engine.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ==================== Geography Models ====================

@dataclass
class GeographyInput:
    """
    Defines a geographic location for community analysis.
    Can be as broad as state or as narrow as census tract.
    """
    state: str
    county: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    census_tract: Optional[str] = None
    borough: Optional[str] = None  # For NYC


# ==================== Community Data Models ====================

@dataclass
class DemographicProfile:
    """Demographic composition of a community."""
    total_population: int
    median_age: float

    # Race/Ethnicity distribution (percentages)
    pct_white: float
    pct_black: float
    pct_hispanic: float
    pct_asian: float
    pct_native_american: float
    pct_other: float

    # Minority majority indicator
    pct_minority: float  # Combined non-white
    is_majority_minority: bool


@dataclass
class EconomicProfile:
    """Economic indicators for a community."""
    median_household_income: float
    area_median_income: float  # HUD AMI
    ami_ratio: float  # median_income / AMI

    per_capita_income: float
    poverty_rate: float
    unemployment_rate: float

    # Income distribution
    pct_below_50k: float
    pct_50k_to_100k: float
    pct_100k_to_200k: float
    pct_above_200k: float


@dataclass
class HousingProfile:
    """Housing market characteristics."""
    total_housing_units: int
    homeownership_rate: float  # % owner-occupied
    rental_rate: float  # % renter-occupied
    vacancy_rate: float

    median_home_value: float
    median_rent: float
    rent_burden_rate: float  # % paying >30% income on rent
    severe_rent_burden_rate: float  # % paying >50% income on rent

    # Housing stock composition
    pct_single_family: float
    pct_2_4_units: float
    pct_5plus_units: float
    pct_condo: float
    pct_manufactured: float

    # Market conditions
    is_high_cost_area: bool
    conforming_loan_limit: float
    high_balance_loan_limit: Optional[float] = None


@dataclass
class CreditProfile:
    """Credit characteristics of community residents."""
    avg_credit_score: float
    median_credit_score: float

    # Credit score distribution
    pct_below_580: float  # Deep subprime
    pct_580_to_619: float  # Subprime
    pct_620_to_679: float  # Near-prime
    pct_680_to_739: float  # Prime
    pct_740_plus: float  # Super-prime

    avg_dti_ratio: float
    pct_high_dti: float  # DTI > 43%

    # Credit issues
    foreclosure_rate: float  # Per 1000 households
    bankruptcy_rate: float  # Per 1000 households
    collection_rate: float  # % with collections


@dataclass
class MortgageMarketProfile:
    """Mortgage market activity and patterns."""
    total_applications: int
    approval_rate: float
    denial_rate: float
    withdrawal_rate: float

    # Denial reasons (top factors)
    top_denial_reasons: List[str]

    # Loan types (distribution)
    pct_conventional: float
    pct_fha: float
    pct_va: float
    pct_usda: float

    # Purpose distribution
    pct_purchase: float
    pct_refinance: float
    pct_cash_out: float

    # First-time homebuyer estimate
    estimated_fthb_rate: float

    # Average loan characteristics
    avg_loan_amount: float
    avg_ltv: float
    avg_dti: float
    avg_rate: float


@dataclass
class UnderservedSignals:
    """Signals indicating an underserved community."""
    low_homeownership: bool  # < 45%
    high_rent_burden: bool  # > 30% severe burden
    high_denial_rate: bool  # > 25%
    low_ami_ratio: bool  # < 0.80
    majority_minority: bool  # > 50% non-white
    persistent_poverty: bool  # Poverty > 20%
    low_credit_cluster: bool  # Avg < 680
    high_fthb_demand: bool  # > 40% FTHB
    high_foreclosure_rate: bool  # > 5 per 1000

    # Aggregate score
    signal_count: int
    severity_level: str  # "Low", "Moderate", "High", "Severe"


@dataclass
class CommunityProfile:
    """Complete profile of a community."""
    geography: GeographyInput
    name: str  # Human-readable location name

    demographics: DemographicProfile
    economics: EconomicProfile
    housing: HousingProfile
    credit: CreditProfile
    mortgage_market: MortgageMarketProfile
    underserved_signals: UnderservedSignals

    # Computed underserved index (0-100)
    underserved_index: float
    underserved_classification: str  # "Stable", "At-Risk", "Underserved", "Severely Underserved"

    # Key insights
    key_challenges: List[str]
    key_opportunities: List[str]


# ==================== Persona Models ====================

@dataclass
class BorrowerPersona:
    """Typical borrower profile for a community."""
    persona_name: str  # e.g., "Harlem First-Time Buyer"
    description: str

    # Demographics
    typical_age_range: Tuple[int, int]
    household_type: str  # "Single", "Couple", "Family", "Multi-generational"

    # Financial profile
    income_range: Tuple[float, float]
    typical_credit_score: int
    typical_dti: float
    typical_debt_amount: float

    # Down payment capacity
    typical_down_payment_pct: float
    typical_down_payment_amount: float
    needs_dpa: bool  # Down Payment Assistance

    # Housing search
    target_home_price: float
    target_loan_amount: float
    preferred_property_types: List[str]

    # Challenges
    main_barriers: List[str]
    education_needs: List[str]

    # Characteristics
    likely_first_time_buyer: bool
    likely_needs_credit_repair: bool
    likely_needs_manual_uw: bool
    likely_bilingual_services: bool


# ==================== Recommendation Models ====================

class MortgageProgram(Enum):
    """Available mortgage programs."""
    CONVENTIONAL_STANDARD = "Conventional Standard"
    CONVENTIONAL_97 = "Conventional 97% LTV (FTHB)"
    HOMEREADY = "HomeReady (LMI/Underserved)"
    HOME_POSSIBLE = "Home Possible (LMI/Underserved)"
    FHA_STANDARD = "FHA Standard"
    FHA_203K = "FHA 203(k) Rehab"
    VA = "VA Loan"
    USDA = "USDA Rural Development"
    HIGH_BALANCE = "High-Balance Conforming"
    JUMBO = "Jumbo"


@dataclass
class ProgramRecommendation:
    """Recommendation for a specific mortgage program."""
    program: MortgageProgram
    priority: int  # 1 = highest
    rationale: str

    # Fit scores (0-100)
    credit_fit: float
    income_fit: float
    ltv_fit: float
    market_fit: float
    overall_fit: float

    # Key features
    max_ltv: float
    min_credit_score: int
    requires_mi: bool
    mi_strategy: str

    # Special features
    ami_requirement: Optional[float] = None
    fthb_requirement: bool = False
    education_requirement: bool = False
    allows_dpa: bool = True

    # Estimated terms
    estimated_rate_range: Tuple[float, float] = (0.0, 0.0)
    estimated_llpa_range: Tuple[float, float] = (0.0, 0.0)


@dataclass
class CommunityMortgageRecommendation:
    """Tailored mortgage recommendations for a community."""
    community_name: str
    persona: BorrowerPersona

    # Recommended programs (ranked)
    recommended_programs: List[ProgramRecommendation]

    # Optimal program
    optimal_program: ProgramRecommendation

    # Strategy recommendations
    ltv_strategy: str
    mi_strategy: str
    reserves_strategy: str
    rate_strategy: str

    # Risk considerations
    hpml_risk: bool
    hoepa_risk: bool
    high_dti_considerations: str

    # LLPA optimization
    available_waivers: List[str]
    llpa_reduction_strategies: List[str]


# ==================== Pricing Models ====================

@dataclass
class CommunityPricingRecommendation:
    """Pricing analysis for community-typical loan."""
    base_scenario: Dict  # ScenarioInput as dict

    # Pricing results from 16-rule engine
    eligibility_overall: bool
    calculated_ltv: float
    calculated_dti: float

    # Pricing
    base_rate: float
    base_price: float
    llpa_total_bps: float
    net_price: float

    # Components
    llpa_components: List[Dict]
    waivers_applied: List[str]

    # Optimizations available
    potential_improvements: List[str]
    estimated_savings_bps: float


# ==================== Quick Serve Models ====================

@dataclass
class OutreachStrategy:
    """Community outreach recommendations."""
    target_channels: List[str]  # Churches, community centers, social media, etc.
    partnership_opportunities: List[str]
    language_needs: List[str]
    cultural_considerations: List[str]

    key_messages: List[str]
    trust_building_tactics: List[str]


@dataclass
class EducationModules:
    """Required borrower education."""
    homebuyer_education: bool
    credit_education: bool
    budget_counseling: bool
    debt_management: bool

    recommended_courses: List[str]
    estimated_timeline: str  # e.g., "2-3 months"


@dataclass
class PrequalificationWorkflow:
    """Streamlined prequalification process."""
    required_documents: List[str]
    alternative_credit_sources: List[str]  # Rent, utilities, etc.
    fast_track_criteria: List[str]
    manual_uw_triggers: List[str]

    typical_timeline: str
    approval_probability: float


@dataclass
class CreditOptimization:
    """Credit repair and optimization strategies."""
    common_issues: List[str]
    quick_wins: List[str]  # e.g., pay down specific cards
    timeline_to_loan_ready: str
    referral_partners: List[str]  # Credit counseling orgs


@dataclass
class DPAIntegration:
    """Down Payment Assistance opportunities."""
    available_programs: List[str]
    typical_assistance_amount: float
    eligibility_requirements: List[str]
    application_process: str


@dataclass
class QuickServePlan:
    """Complete quick-serve strategy for community."""
    community_name: str

    # Strategy components
    outreach: OutreachStrategy
    education: EducationModules
    prequalification: PrequalificationWorkflow
    credit_optimization: CreditOptimization
    dpa_integration: DPAIntegration

    # Operational recommendations
    dedicated_loan_officers: int
    multilingual_staff_needed: List[str]
    technology_tools: List[str]
    processing_time_target: str

    # Success metrics
    target_approval_rate: float
    target_volume_per_month: int
    estimated_community_impact: str


# ==================== Engine Output Models ====================

@dataclass
class CommunityInsightResult:
    """Complete output from CommunityInsightEngine."""
    geography: GeographyInput

    # Analysis components
    community_profile: CommunityProfile
    borrower_persona: BorrowerPersona
    mortgage_recommendation: CommunityMortgageRecommendation
    pricing_recommendation: CommunityPricingRecommendation
    quick_serve_plan: QuickServePlan

    # Summary
    executive_summary: str
    action_items: List[str]

    # Metadata
    analysis_timestamp: str
    data_sources: List[str]
    confidence_score: float  # 0-100
