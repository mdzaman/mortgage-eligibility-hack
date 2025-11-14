"""
Community Mortgage Recommendations Engine

Generates tailored mortgage program recommendations and quick-serve plans
for underserved communities.
"""

from typing import List, Tuple
from models_community import (
    CommunityProfile, BorrowerPersona,
    MortgageProgram, ProgramRecommendation,
    CommunityMortgageRecommendation,
    OutreachStrategy, EducationModules,
    PrequalificationWorkflow, CreditOptimization,
    DPAIntegration, QuickServePlan
)


# ==================== Program Fit Scoring ====================

def calculate_credit_fit(credit_score: int, program: MortgageProgram) -> float:
    """Calculate how well borrower credit fits program (0-100)."""
    # Define minimum credit scores by program
    min_scores = {
        MortgageProgram.CONVENTIONAL_STANDARD: 620,
        MortgageProgram.CONVENTIONAL_97: 620,
        MortgageProgram.HOMEREADY: 620,
        MortgageProgram.HOME_POSSIBLE: 660,
        MortgageProgram.FHA_STANDARD: 580,
        MortgageProgram.FHA_203K: 580,
        MortgageProgram.VA: 580,
        MortgageProgram.USDA: 640,
        MortgageProgram.HIGH_BALANCE: 680,
        MortgageProgram.JUMBO: 700
    }

    min_score = min_scores.get(program, 620)

    if credit_score < min_score:
        # Below minimum - poor fit
        gap = min_score - credit_score
        return max(0, 50 - (gap / 2))  # Lose 1 point per 2 credit points below
    elif credit_score >= min_score + 60:
        # Well above minimum - excellent fit
        return 100
    else:
        # Above minimum - scale linearly
        excess = credit_score - min_score
        return 50 + (excess / 60) * 50


def calculate_income_fit(ami_ratio: float, program: MortgageProgram) -> float:
    """Calculate how well income fits program (0-100)."""
    # Programs with income limits get higher fit for lower income
    income_sensitive = {
        MortgageProgram.HOMEREADY: True,
        MortgageProgram.HOME_POSSIBLE: True,
        MortgageProgram.USDA: True,
        MortgageProgram.FHA_STANDARD: False,
        MortgageProgram.CONVENTIONAL_97: True  # Gets benefits at lower AMI
    }

    if program not in income_sensitive or not income_sensitive[program]:
        # No income restrictions - perfect fit
        return 100

    # For income-sensitive programs
    if ami_ratio <= 0.80:
        return 100  # Ideal for these programs
    elif ami_ratio <= 1.00:
        return 75  # Still good fit
    elif ami_ratio <= 1.15:
        return 50 if program == MortgageProgram.USDA else 25
    else:
        return 10  # May not qualify


def calculate_ltv_fit(typical_ltv: float, program: MortgageProgram) -> float:
    """Calculate how well LTV fits program (0-100)."""
    # Define optimal LTV ranges by program
    if program in [MortgageProgram.CONVENTIONAL_97, MortgageProgram.FHA_STANDARD]:
        # High LTV programs
        if typical_ltv >= 95:
            return 100
        elif typical_ltv >= 90:
            return 90
        else:
            return 70
    elif program in [MortgageProgram.HOMEREADY, MortgageProgram.HOME_POSSIBLE]:
        # Flexible LTV
        if typical_ltv >= 95:
            return 100
        elif typical_ltv >= 90:
            return 95
        else:
            return 85
    elif program == MortgageProgram.VA:
        # 100% LTV possible
        return 100
    else:
        # Standard programs prefer lower LTV
        if typical_ltv <= 80:
            return 100
        elif typical_ltv <= 90:
            return 80
        elif typical_ltv <= 95:
            return 60
        else:
            return 40


def calculate_market_fit(profile: CommunityProfile, program: MortgageProgram) -> float:
    """Calculate how well program fits community market (0-100)."""
    market = profile.mortgage_market
    housing = profile.housing
    signals = profile.underserved_signals

    # Check existing market penetration
    penetration = {
        MortgageProgram.FHA_STANDARD: market.pct_fha,
        MortgageProgram.FHA_203K: market.pct_fha,
        MortgageProgram.VA: market.pct_va,
        MortgageProgram.USDA: market.pct_usda,
        MortgageProgram.CONVENTIONAL_STANDARD: market.pct_conventional,
        MortgageProgram.CONVENTIONAL_97: market.pct_conventional,
        MortgageProgram.HOMEREADY: market.pct_conventional,
        MortgageProgram.HOME_POSSIBLE: market.pct_conventional
    }

    base_score = penetration.get(program, 0)

    # Adjust for community characteristics
    if program in [MortgageProgram.HOMEREADY, MortgageProgram.HOME_POSSIBLE]:
        if signals.low_ami_ratio:
            base_score += 40
        if signals.high_fthb_demand:
            base_score += 20

    if program == MortgageProgram.FHA_STANDARD:
        if signals.low_credit_cluster:
            base_score += 30
        if signals.high_fthb_demand:
            base_score += 20

    if program == MortgageProgram.FHA_203K:
        # Property condition issues common in underserved areas
        if housing.median_home_value < 150_000:
            base_score += 40

    if program == MortgageProgram.HIGH_BALANCE:
        if housing.is_high_cost_area and housing.median_home_value > 700_000:
            base_score += 50

    return min(base_score, 100)


def calculate_overall_fit(credit_fit: float, income_fit: float,
                         ltv_fit: float, market_fit: float) -> float:
    """Calculate weighted overall fit score."""
    return (
        credit_fit * 0.30 +
        income_fit * 0.25 +
        ltv_fit * 0.25 +
        market_fit * 0.20
    )


# ==================== Program Recommendations ====================

def create_program_recommendation(
    program: MortgageProgram,
    profile: CommunityProfile,
    persona: BorrowerPersona
) -> ProgramRecommendation:
    """Create detailed recommendation for a specific program."""

    # Calculate fit scores
    credit_fit = calculate_credit_fit(persona.typical_credit_score, program)
    income_fit = calculate_income_fit(profile.economics.ami_ratio, program)

    typical_ltv = (persona.target_loan_amount / persona.target_home_price) * 100
    ltv_fit = calculate_ltv_fit(typical_ltv, program)

    market_fit = calculate_market_fit(profile, program)

    overall_fit = calculate_overall_fit(credit_fit, income_fit, ltv_fit, market_fit)

    # Define program characteristics
    program_specs = {
        MortgageProgram.CONVENTIONAL_97: {
            "max_ltv": 97.0,
            "min_credit": 620,
            "requires_mi": True,
            "mi_strategy": "Standard MI required, may qualify for reduced coverage",
            "ami_requirement": None,
            "fthb_requirement": True,
            "education_requirement": True,
            "allows_dpa": True,
            "rate_range": (6.50, 7.00),
            "llpa_range": (-0.25, 0.50),
            "rationale": "Conventional 97% LTV ideal for first-time buyers with good credit and AMI qualification"
        },
        MortgageProgram.HOMEREADY: {
            "max_ltv": 97.0,
            "min_credit": 620,
            "requires_mi": True,
            "mi_strategy": "Standard MI, LLPA waivers available for underserved areas",
            "ami_requirement": 1.00,  # 100% AMI or underserved census tract
            "fthb_requirement": False,
            "education_requirement": True,
            "allows_dpa": True,
            "rate_range": (6.375, 6.875),
            "llpa_range": (-0.50, 0.25),
            "rationale": "HomeReady offers LLPA waivers and flexible underwriting for low-moderate income borrowers"
        },
        MortgageProgram.FHA_STANDARD: {
            "max_ltv": 96.5,
            "min_credit": 580,
            "requires_mi": True,
            "mi_strategy": "MIP required (1.75% upfront + 0.55-0.85% annual)",
            "ami_requirement": None,
            "fthb_requirement": False,
            "education_requirement": False,
            "allows_dpa": True,
            "rate_range": (6.50, 7.25),
            "llpa_range": (0.00, 0.00),
            "rationale": "FHA accepts lower credit scores and higher DTI, ideal for credit-challenged borrowers"
        },
        MortgageProgram.VA: {
            "max_ltv": 100.0,
            "min_credit": 580,
            "requires_mi": False,
            "mi_strategy": "No MI required, funding fee applies (2.15% first-time, waived for disabled)",
            "ami_requirement": None,
            "fthb_requirement": False,
            "education_requirement": False,
            "allows_dpa": True,
            "rate_range": (6.25, 6.75),
            "llpa_range": (0.00, 0.00),
            "rationale": "VA loans offer 100% financing with no MI for veterans and active duty"
        },
        MortgageProgram.HIGH_BALANCE: {
            "max_ltv": 95.0,
            "min_credit": 680,
            "requires_mi": True,
            "mi_strategy": "Standard MI with higher rates for loan amounts above conforming",
            "ami_requirement": None,
            "fthb_requirement": False,
            "education_requirement": False,
            "allows_dpa": False,
            "rate_range": (6.75, 7.50),
            "llpa_range": (0.50, 1.50),
            "rationale": "High-balance for expensive markets where home prices exceed conforming limits"
        }
    }

    specs = program_specs.get(program, program_specs[MortgageProgram.FHA_STANDARD])

    return ProgramRecommendation(
        program=program,
        priority=0,  # Will be set when ranking
        rationale=specs["rationale"],
        credit_fit=credit_fit,
        income_fit=income_fit,
        ltv_fit=ltv_fit,
        market_fit=market_fit,
        overall_fit=overall_fit,
        max_ltv=specs["max_ltv"],
        min_credit_score=specs["min_credit"],
        requires_mi=specs["requires_mi"],
        mi_strategy=specs["mi_strategy"],
        ami_requirement=specs.get("ami_requirement"),
        fthb_requirement=specs.get("fthb_requirement", False),
        education_requirement=specs.get("education_requirement", False),
        allows_dpa=specs.get("allows_dpa", True),
        estimated_rate_range=specs["rate_range"],
        estimated_llpa_range=specs["llpa_range"]
    )


def rank_programs(profile: CommunityProfile,
                 persona: BorrowerPersona) -> List[ProgramRecommendation]:
    """Rank all applicable mortgage programs for the community."""

    # Determine which programs to evaluate
    programs_to_evaluate = [
        MortgageProgram.HOMEREADY,
        MortgageProgram.FHA_STANDARD,
        MortgageProgram.CONVENTIONAL_97,
    ]

    # Add VA if significant veteran population
    if profile.mortgage_market.pct_va > 3:
        programs_to_evaluate.append(MortgageProgram.VA)

    # Add high-balance if high-cost area
    if profile.housing.is_high_cost_area and profile.housing.median_home_value > 700_000:
        programs_to_evaluate.append(MortgageProgram.HIGH_BALANCE)

    # Add 203(k) if older housing stock
    if profile.housing.median_home_value < 200_000:
        programs_to_evaluate.append(MortgageProgram.FHA_203K)

    # Create recommendations
    recommendations = []
    for program in programs_to_evaluate:
        rec = create_program_recommendation(program, profile, persona)
        recommendations.append(rec)

    # Sort by overall fit (descending)
    recommendations.sort(key=lambda x: x.overall_fit, reverse=True)

    # Assign priorities
    for i, rec in enumerate(recommendations):
        rec.priority = i + 1

    return recommendations


# ==================== LLPA Strategies ====================

def generate_llpa_strategies(profile: CommunityProfile,
                            persona: BorrowerPersona) -> List[str]:
    """Generate LLPA reduction strategies."""
    strategies = []

    if persona.likely_first_time_buyer:
        strategies.append(
            "FTHB LLPA waiver available: -0.25% to -0.75% on credit/LTV grid"
        )

    if profile.underserved_signals.low_ami_ratio:
        strategies.append(
            "AMI-based waiver for HomeReady/HomePossible: Additional -0.25% to -0.50%"
        )

    if profile.underserved_signals.majority_minority:
        strategies.append(
            "Underserved census tract designation may qualify for additional waivers"
        )

    if persona.typical_credit_score >= 720:
        strategies.append(
            "Target credit scores 720+ for lower LLPA tiers"
        )

    if persona.typical_down_payment_pct < 10:
        strategies.append(
            "Consider down payment assistance to reduce LTV and lower LLPAs"
        )

    return strategies


def identify_available_waivers(profile: CommunityProfile,
                              persona: BorrowerPersona) -> List[str]:
    """Identify available LLPA waivers."""
    waivers = []

    if persona.likely_first_time_buyer:
        waivers.append("First-Time Homebuyer waiver")

    if profile.economics.ami_ratio < 1.00:
        waivers.append("Area Median Income waiver (AMI ≤ 100%)")

    if profile.underserved_signals.majority_minority:
        waivers.append("Underserved area designation")

    return waivers


# ==================== Quick Serve Plan ====================

def create_outreach_strategy(profile: CommunityProfile) -> OutreachStrategy:
    """Create community outreach strategy."""

    channels = [
        "Community centers and churches",
        "Local schools and libraries",
        "Social media (Facebook, Instagram community groups)",
        "Community events and festivals"
    ]

    partnerships = [
        "Local housing counseling agencies",
        "Community development financial institutions (CDFIs)",
        "Non-profit housing organizations",
        "Faith-based organizations"
    ]

    if profile.housing.is_high_cost_area:
        partnerships.append("Municipal housing authorities")

    # Language needs
    languages = ["English"]
    if profile.demographics.pct_hispanic > 20:
        languages.append("Spanish")
    if profile.demographics.pct_asian > 10:
        languages.append("Chinese, Korean, or other Asian languages")

    cultural_considerations = [
        "Build trust through community presence and long-term relationships",
        "Offer in-person consultations in the community",
        "Partner with trusted local organizations"
    ]

    if profile.underserved_signals.majority_minority:
        cultural_considerations.append(
            "Ensure diverse loan officer team that reflects community demographics"
        )

    key_messages = [
        f"Homeownership is achievable with incomes starting at ${profile.economics.median_household_income:,.0f}",
        "Down payment assistance available",
        "Credit scores as low as 580-620 may qualify"
    ]

    trust_tactics = [
        "Success stories from community residents",
        "Free homebuyer education workshops",
        "No-obligation pre-qualification consultations",
        "Transparent fee structure and process"
    ]

    return OutreachStrategy(
        target_channels=channels,
        partnership_opportunities=partnerships,
        language_needs=languages,
        cultural_considerations=cultural_considerations,
        key_messages=key_messages,
        trust_building_tactics=trust_tactics
    )


def create_education_modules(profile: CommunityProfile,
                            persona: BorrowerPersona) -> EducationModules:
    """Create borrower education plan."""

    homebuyer_ed = persona.likely_first_time_buyer
    credit_ed = profile.underserved_signals.low_credit_cluster
    budget_counseling = profile.underserved_signals.high_rent_burden
    debt_mgmt = profile.credit.avg_dti_ratio > 43

    courses = []
    if homebuyer_ed:
        courses.append("HUD-approved 8-hour First-Time Homebuyer Course")
    if credit_ed:
        courses.append("Credit Building and Repair Workshop")
    if budget_counseling:
        courses.append("Financial Literacy and Budgeting")
    if debt_mgmt:
        courses.append("Debt Management Strategies")

    timeline = "2-4 months" if credit_ed else "1-2 months"

    return EducationModules(
        homebuyer_education=homebuyer_ed,
        credit_education=credit_ed,
        budget_counseling=budget_counseling,
        debt_management=debt_mgmt,
        recommended_courses=courses,
        estimated_timeline=timeline
    )


def create_prequalification_workflow(profile: CommunityProfile,
                                     persona: BorrowerPersona) -> PrequalificationWorkflow:
    """Create streamlined prequalification workflow."""

    required_docs = [
        "Photo ID",
        "2 years tax returns",
        "2 months pay stubs",
        "2 months bank statements",
        "Credit report authorization"
    ]

    alternative_credit = []
    if persona.likely_needs_credit_repair:
        alternative_credit = [
            "12 months rent payment history",
            "Utility payment history (electric, gas, phone)",
            "Insurance payment history",
            "Other recurring payments"
        ]

    fast_track = []
    if persona.typical_credit_score >= 680:
        fast_track.append("Credit score 680+ with stable employment")
    if not persona.needs_dpa:
        fast_track.append("10%+ down payment without assistance")

    manual_uw_triggers = []
    if persona.typical_credit_score < 660:
        manual_uw_triggers.append("Credit score below 660")
    if profile.credit.pct_high_dti > 40:
        manual_uw_triggers.append("DTI above 43%")
    if persona.likely_needs_credit_repair:
        manual_uw_triggers.append("Limited or non-traditional credit history")

    timeline = "3-5 days for initial pre-qualification, 30-45 days to close"

    # Estimate approval probability
    approval_prob = min(100 - profile.mortgage_market.denial_rate, 75)

    return PrequalificationWorkflow(
        required_documents=required_docs,
        alternative_credit_sources=alternative_credit,
        fast_track_criteria=fast_track,
        manual_uw_triggers=manual_uw_triggers,
        typical_timeline=timeline,
        approval_probability=approval_prob
    )


def create_credit_optimization(profile: CommunityProfile) -> CreditOptimization:
    """Create credit optimization strategy."""

    common_issues = []
    if profile.credit.collection_rate > 25:
        common_issues.append("Collections and charge-offs")
    if profile.credit.pct_high_dti > 35:
        common_issues.append("High credit card utilization")
    if profile.credit.foreclosure_rate > 3:
        common_issues.append("Prior foreclosure or bankruptcy")

    quick_wins = [
        "Pay down credit card balances below 30% utilization",
        "Dispute and remove errors from credit report",
        "Become authorized user on established account"
    ]

    if profile.credit.collection_rate > 25:
        quick_wins.append("Pay for delete negotiations on collections")

    timeline = "3-6 months for significant improvement"
    if profile.credit.avg_credit_score < 600:
        timeline = "6-12 months for loan-ready credit"

    referral_partners = [
        "Non-profit credit counseling agencies (NFCC members)",
        "HUD-approved housing counselors",
        "Local community development financial institutions"
    ]

    return CreditOptimization(
        common_issues=common_issues,
        quick_wins=quick_wins,
        timeline_to_loan_ready=timeline,
        referral_partners=referral_partners
    )


def create_dpa_integration(profile: CommunityProfile,
                          persona: BorrowerPersona) -> DPAIntegration:
    """Create down payment assistance integration plan."""

    programs = []

    # State programs
    if profile.geography.state == "NY":
        programs.append("NYS Affordable Housing Corporation programs")
        programs.append("SONYMA (State of NY Mortgage Agency)")

    # City/County programs
    if profile.geography.city == "New York":
        programs.append("NYC Housing Development Corporation (HDC)")
        programs.append("NYC Department of Housing Preservation & Development (HPD)")
    elif profile.geography.city == "Buffalo":
        programs.append("Buffalo Urban Development Corporation")

    # National programs
    programs.append("Chenoa Fund")
    programs.append("Down Payment Assistance through lender")

    typical_amount = persona.typical_down_payment_amount * 0.5  # Cover ~50% of down payment

    requirements = [
        f"Income at or below {profile.economics.ami_ratio * 100:.0f}% AMI",
        "First-time homebuyer (typically)",
        "Complete homebuyer education",
        "Occupy as primary residence"
    ]

    process = "Application through participating lender, typically adds 1-2 weeks to timeline"

    return DPAIntegration(
        available_programs=programs,
        typical_assistance_amount=typical_amount,
        eligibility_requirements=requirements,
        application_process=process
    )


def create_quick_serve_plan(profile: CommunityProfile,
                           persona: BorrowerPersona,
                           recommendations: List[ProgramRecommendation]) -> QuickServePlan:
    """Create complete quick-serve implementation plan."""

    outreach = create_outreach_strategy(profile)
    education = create_education_modules(profile, persona)
    prequalification = create_prequalification_workflow(profile, persona)
    credit_opt = create_credit_optimization(profile)
    dpa = create_dpa_integration(profile, persona)

    # Operational recommendations
    population = profile.demographics.total_population
    dedicated_los = max(1, int(population / 25_000))  # 1 LO per 25k population

    multilingual = []
    if "Spanish" in outreach.language_needs:
        multilingual.append("Spanish")
    if profile.demographics.pct_asian > 10:
        multilingual.append("Asian languages")

    tech_tools = [
        "Digital mortgage application platform",
        "Document upload portal",
        "Automated pre-qualification system",
        "CRM with community tracking"
    ]

    processing_target = "30-45 days from application to closing"

    # Success metrics
    target_approval = min(85, prequalification.approval_probability + 15)
    target_volume = int((profile.mortgage_market.total_applications * 0.15) / 12)  # 15% market share monthly

    impact = (
        f"Potential to serve {target_volume * 12} families annually, "
        f"contributing ${target_volume * 12 * persona.target_loan_amount:,.0f} "
        f"in homeownership financing to {profile.name}"
    )

    return QuickServePlan(
        community_name=profile.name,
        outreach=outreach,
        education=education,
        prequalification=prequalification,
        credit_optimization=credit_opt,
        dpa_integration=dpa,
        dedicated_loan_officers=dedicated_los,
        multilingual_staff_needed=multilingual,
        technology_tools=tech_tools,
        processing_time_target=processing_target,
        target_approval_rate=target_approval,
        target_volume_per_month=target_volume,
        estimated_community_impact=impact
    )


# ==================== Main Recommendation Generator ====================

def generate_mortgage_recommendation(
    profile: CommunityProfile,
    persona: BorrowerPersona
) -> CommunityMortgageRecommendation:
    """Generate complete mortgage recommendation for community."""

    # Rank programs
    ranked_programs = rank_programs(profile, persona)
    optimal_program = ranked_programs[0]

    # Determine strategies
    typical_ltv = (persona.target_loan_amount / persona.target_home_price) * 100

    if typical_ltv > 95:
        ltv_strategy = "High LTV (95-97%) with MI, focus on FHA or HomeReady/Conventional 97%"
    elif typical_ltv > 90:
        ltv_strategy = "High LTV (90-95%) with MI, multiple options available"
    else:
        ltv_strategy = "Moderate LTV (<90%), conventional options preferred"

    if persona.needs_dpa:
        mi_strategy = "Required at high LTV. Recommend borrower-paid monthly for flexibility. Explore reduced MI options."
    else:
        mi_strategy = "Standard MI required above 80% LTV. Consider lender-paid MI if rate-sensitive."

    if profile.housing.median_home_value < 200_000:
        reserves_strategy = "Minimal reserves required (0-2 months). Focus on down payment savings."
    else:
        reserves_strategy = "2-6 months reserves recommended based on property type and loan amount."

    rate_strategy = (
        f"Target rates {optimal_program.estimated_rate_range[0]:.3f}% - "
        f"{optimal_program.estimated_rate_range[1]:.3f}% with optimal program"
    )

    # Risk assessments
    hpml_risk = False
    if persona.typical_credit_score < 640:
        hpml_risk = True

    hoepa_risk = False  # Rare for purchase mortgages

    dti_considerations = (
        f"Average DTI {persona.typical_dti:.1f}%. "
        f"Manual underwriting common. Focus on compensating factors: "
        f"stable employment, cash reserves, residual income."
    )

    # LLPA strategies
    llpa_strategies = generate_llpa_strategies(profile, persona)
    available_waivers = identify_available_waivers(profile, persona)

    return CommunityMortgageRecommendation(
        community_name=profile.name,
        persona=persona,
        recommended_programs=ranked_programs,
        optimal_program=optimal_program,
        ltv_strategy=ltv_strategy,
        mi_strategy=mi_strategy,
        reserves_strategy=reserves_strategy,
        rate_strategy=rate_strategy,
        hpml_risk=hpml_risk,
        hoepa_risk=hoepa_risk,
        high_dti_considerations=dti_considerations,
        available_waivers=available_waivers,
        llpa_reduction_strategies=llpa_strategies
    )
