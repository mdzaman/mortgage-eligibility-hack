"""
Community Borrower Persona Generator

Generates typical borrower personas from community profiles.
Personas represent the most common borrower characteristics in a given community.
"""

from typing import List, Tuple
from models_community import (
    CommunityProfile, BorrowerPersona,
    DemographicProfile, EconomicProfile, HousingProfile,
    CreditProfile, MortgageMarketProfile
)


def generate_persona_name(geography_name: str, signals) -> str:
    """Generate descriptive persona name."""
    if signals.high_fthb_demand:
        return f"{geography_name} First-Time Homebuyer"
    elif signals.low_credit_cluster:
        return f"{geography_name} Credit-Building Buyer"
    elif signals.low_ami_ratio:
        return f"{geography_name} Low-Moderate Income Buyer"
    else:
        return f"{geography_name} Aspiring Homeowner"


def determine_age_range(demographics: DemographicProfile) -> Tuple[int, int]:
    """Determine typical age range for buyers."""
    median_age = demographics.median_age

    # Adjust based on median age
    if median_age < 30:
        return (25, 35)
    elif median_age < 35:
        return (28, 40)
    elif median_age < 40:
        return (30, 45)
    else:
        return (35, 50)


def determine_household_type(demographics: DemographicProfile,
                             economics: EconomicProfile) -> str:
    """Determine typical household composition."""
    # Use age and income as proxies
    if demographics.median_age < 32:
        if economics.median_household_income < 40_000:
            return "Single"
        else:
            return "Couple"
    elif demographics.median_age < 40:
        return "Family"
    else:
        return "Multi-generational"


def calculate_income_range(economics: EconomicProfile) -> Tuple[float, float]:
    """Calculate typical income range for homebuyers in community."""
    median = economics.median_household_income

    # Homebuyers typically in 50th-80th percentile of community income
    # Use income distribution to estimate
    if economics.pct_50k_to_100k > 30:
        # Middle-income community
        lower = median * 0.9
        upper = median * 1.5
    elif economics.pct_below_50k > 50:
        # Low-income community
        lower = median * 0.85
        upper = median * 1.3
    else:
        # Mixed or higher-income community
        lower = median * 1.0
        upper = median * 2.0

    return (lower, upper)


def determine_typical_credit_score(credit: CreditProfile,
                                   market: MortgageMarketProfile) -> int:
    """Determine typical credit score for approved borrowers."""
    # Approved borrowers typically have better credit than community avg
    avg = credit.avg_credit_score

    # Adjustment based on loan type mix
    if market.pct_fha > 50:
        # FHA market - credit scores can be lower
        typical = int(avg + 10)
    elif market.pct_conventional > 50:
        # Conventional market - credit scores higher
        typical = int(avg + 30)
    else:
        # Mixed market
        typical = int(avg + 20)

    # Clamp to reasonable range
    return max(580, min(850, typical))


def calculate_typical_dti(credit: CreditProfile,
                         market: MortgageMarketProfile) -> float:
    """Calculate typical DTI for approved borrowers."""
    # Use market average as baseline
    return market.avg_dti


def calculate_typical_debt(economics: EconomicProfile,
                          credit: CreditProfile) -> float:
    """Estimate typical debt amount."""
    monthly_income = economics.median_household_income / 12
    typical_dti = credit.avg_dti_ratio / 100
    return monthly_income * typical_dti


def calculate_down_payment_capacity(economics: EconomicProfile,
                                    housing: HousingProfile,
                                    signals) -> Tuple[float, float, bool]:
    """
    Calculate typical down payment percentage and amount.
    Returns (pct, amount, needs_dpa)
    """
    median_home_value = housing.median_home_value

    # Estimate based on signals
    if signals.high_rent_burden and signals.low_ami_ratio:
        # Very limited savings capacity
        pct = 3.5  # FHA minimum
        needs_dpa = True
    elif signals.low_ami_ratio:
        # Limited savings
        pct = 5.0
        needs_dpa = True
    elif signals.high_fthb_demand:
        # First-time buyers - limited savings but not severe
        pct = 6.0
        needs_dpa = True
    else:
        # Moderate savings capacity
        pct = 10.0
        needs_dpa = False

    amount = median_home_value * (pct / 100)

    return (pct, amount, needs_dpa)


def calculate_target_home_price(housing: HousingProfile,
                                economics: EconomicProfile) -> float:
    """Calculate typical target home price for buyers."""
    # Use median home value, adjusted by affordability
    median = housing.median_home_value

    # If very high rent burden, buyers target lower prices
    if housing.severe_rent_burden_rate > 35:
        return median * 0.85
    # If area is expensive relative to income
    elif economics.ami_ratio < 0.60:
        return median * 0.80
    else:
        return median


def determine_property_preferences(housing: HousingProfile) -> List[str]:
    """Determine preferred property types based on stock."""
    preferences = []

    # Rank by availability in community
    stock = [
        (housing.pct_single_family, "Single Family"),
        (housing.pct_2_4_units, "2-4 Unit Multi-family"),
        (housing.pct_5plus_units, "Condo/Co-op"),
        (housing.pct_condo, "Condo"),
    ]

    # Sort by percentage (descending)
    stock.sort(reverse=True)

    # Take top 2-3 types
    for pct, prop_type in stock[:3]:
        if pct > 5:  # Only include if > 5% of stock
            preferences.append(prop_type)

    return preferences if preferences else ["Single Family"]


def identify_barriers(credit: CreditProfile,
                     economics: EconomicProfile,
                     housing: HousingProfile,
                     signals) -> List[str]:
    """Identify main barriers to homeownership."""
    barriers = []

    if signals.low_credit_cluster:
        barriers.append("Credit score below conventional thresholds")

    if signals.high_rent_burden:
        barriers.append("High rent burden limiting savings capacity")

    if signals.low_ami_ratio:
        barriers.append("Income significantly below area median")

    if credit.pct_high_dti > 40:
        barriers.append("High existing debt-to-income ratios")

    if housing.median_home_value > (economics.median_household_income * 5):
        barriers.append("Home prices high relative to income")

    if credit.foreclosure_rate > 5:
        barriers.append("Prior foreclosure or bankruptcy history common")

    if credit.collection_rate > 30:
        barriers.append("Collections and derogatory credit common")

    return barriers


def identify_education_needs(signals,
                             credit: CreditProfile,
                             market: MortgageMarketProfile) -> List[str]:
    """Identify borrower education needs."""
    needs = []

    if signals.high_fthb_demand:
        needs.append("First-time homebuyer education (8-hour HUD-approved)")

    if signals.low_credit_cluster:
        needs.append("Credit repair and rebuilding strategies")

    if credit.avg_dti_ratio > 43:
        needs.append("Debt management and budgeting")

    if market.denial_rate > 30:
        needs.append("Mortgage application preparation and documentation")

    if signals.low_ami_ratio:
        needs.append("Down payment assistance program navigation")

    needs.append("Homeownership sustainability and foreclosure prevention")

    return needs


def assess_special_needs(demographics: DemographicProfile,
                        credit: CreditProfile,
                        market: MortgageMarketProfile) -> Tuple[bool, bool, bool, bool]:
    """
    Assess special needs for borrower support.
    Returns (is_fthb, needs_credit_repair, needs_manual_uw, needs_bilingual)
    """
    is_fthb = market.estimated_fthb_rate > 50
    needs_credit_repair = credit.avg_credit_score < 650
    needs_manual_uw = credit.avg_credit_score < 660 or credit.pct_high_dti > 40

    # Bilingual if >30% Hispanic or >20% Asian
    needs_bilingual = demographics.pct_hispanic > 30 or demographics.pct_asian > 20

    return (is_fthb, needs_credit_repair, needs_manual_uw, needs_bilingual)


def generate_borrower_persona(profile: CommunityProfile) -> BorrowerPersona:
    """
    Generate typical borrower persona from community profile.
    This represents the most common homebuyer in the community.
    """
    demographics = profile.demographics
    economics = profile.economics
    housing = profile.housing
    credit = profile.credit
    market = profile.mortgage_market
    signals = profile.underserved_signals

    # Generate persona components
    persona_name = generate_persona_name(profile.name, signals)
    age_range = determine_age_range(demographics)
    household_type = determine_household_type(demographics, economics)
    income_range = calculate_income_range(economics)
    typical_credit = determine_typical_credit_score(credit, market)
    typical_dti = calculate_typical_dti(credit, market)
    typical_debt = calculate_typical_debt(economics, credit)

    down_pct, down_amount, needs_dpa = calculate_down_payment_capacity(
        economics, housing, signals
    )

    target_price = calculate_target_home_price(housing, economics)
    target_loan = target_price * (1 - down_pct / 100)

    property_prefs = determine_property_preferences(housing)
    barriers = identify_barriers(credit, economics, housing, signals)
    education_needs = identify_education_needs(signals, credit, market)

    is_fthb, needs_credit_repair, needs_manual_uw, needs_bilingual = assess_special_needs(
        demographics, credit, market
    )

    # Build description
    description = (
        f"Typical homebuyer in {profile.name} is "
        f"age {age_range[0]}-{age_range[1]}, {household_type.lower()} household, "
        f"with income ${income_range[0]:,.0f}-${income_range[1]:,.0f} annually. "
        f"Credit score around {typical_credit}, targeting homes around ${target_price:,.0f}. "
    )

    if needs_dpa:
        description += "Requires down payment assistance. "
    if is_fthb:
        description += "Predominantly first-time homebuyers. "
    if needs_credit_repair:
        description += "Often needs credit improvement support. "

    return BorrowerPersona(
        persona_name=persona_name,
        description=description,
        typical_age_range=age_range,
        household_type=household_type,
        income_range=income_range,
        typical_credit_score=typical_credit,
        typical_dti=typical_dti,
        typical_debt_amount=typical_debt,
        typical_down_payment_pct=down_pct,
        typical_down_payment_amount=down_amount,
        needs_dpa=needs_dpa,
        target_home_price=target_price,
        target_loan_amount=target_loan,
        preferred_property_types=property_prefs,
        main_barriers=barriers,
        education_needs=education_needs,
        likely_first_time_buyer=is_fthb,
        likely_needs_credit_repair=needs_credit_repair,
        likely_needs_manual_uw=needs_manual_uw,
        likely_bilingual_services=needs_bilingual
    )


def generate_scenario_dict(persona: BorrowerPersona,
                          housing: HousingProfile) -> dict:
    """
    Generate a typical loan scenario dictionary from persona.
    Can be used to build ScenarioInput for pricing engine.
    """
    return {
        "credit_score": persona.typical_credit_score,
        "gross_monthly_income": persona.income_range[0] / 12,
        "monthly_debts": persona.typical_debt_amount,
        "liquid_assets": persona.typical_down_payment_amount * 1.1,  # Down payment + reserves
        "purchase_price": persona.target_home_price,
        "appraised_value": persona.target_home_price,
        "loan_amount": persona.target_loan_amount,
        "property_type": "SFR" if "Single Family" in persona.preferred_property_types else "Condo",
        "occupancy": "primary",
        "purpose": "purchase",
        "first_time_homebuyer": persona.likely_first_time_buyer,
        "is_high_cost_area": housing.is_high_cost_area,
        "units": 1
    }
