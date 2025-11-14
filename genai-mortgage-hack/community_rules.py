"""
Community Underserved Detection Rules

Implements rule-based logic to identify underserved communities
and calculate the Underserved Index (0-100 scale).

Formula:
UnderservedIndex =
    (1 - homeownership_rate) * 0.25 +
    rent_burden_score * 0.20 +
    denial_rate_score * 0.20 +
    ami_gap_score * 0.15 +
    credit_gap_score * 0.10 +
    minority_share_score * 0.10

Classifications:
- 80-100: Severely Underserved
- 60-79: Underserved
- 40-59: At-Risk
- 0-39: Stable/Upward Mobility
"""

from models_community import (
    DemographicProfile, EconomicProfile, HousingProfile,
    CreditProfile, MortgageMarketProfile, UnderservedSignals
)


# ==================== Scoring Functions ====================

def score_homeownership(homeownership_rate: float) -> float:
    """
    Score based on homeownership gap.
    Lower homeownership = higher underserved score.

    National avg ~65%, severely underserved <30%
    """
    # Invert: low homeownership = high score
    inverted = (1 - (homeownership_rate / 100.0))
    return min(inverted * 100, 100)


def score_rent_burden(severe_burden_rate: float) -> float:
    """
    Score based on severe rent burden (>50% of income on rent).
    Higher burden = more underserved.

    Threshold: >30% is high
    """
    if severe_burden_rate >= 40:
        return 100
    elif severe_burden_rate >= 30:
        return 75
    elif severe_burden_rate >= 20:
        return 50
    elif severe_burden_rate >= 15:
        return 25
    else:
        return 10


def score_denial_rate(denial_rate: float) -> float:
    """
    Score based on mortgage denial rate.
    Higher denials = more underserved.

    National avg ~10-15%, severely underserved >40%
    """
    if denial_rate >= 50:
        return 100
    elif denial_rate >= 40:
        return 85
    elif denial_rate >= 30:
        return 65
    elif denial_rate >= 20:
        return 40
    else:
        return (denial_rate / 20) * 40


def score_ami_gap(ami_ratio: float) -> float:
    """
    Score based on income gap relative to Area Median Income.
    Lower AMI ratio = more underserved.

    ami_ratio = median_income / area_median_income
    """
    if ami_ratio < 0.50:
        return 100
    elif ami_ratio < 0.60:
        return 85
    elif ami_ratio < 0.70:
        return 65
    elif ami_ratio < 0.80:
        return 45
    elif ami_ratio < 0.90:
        return 25
    else:
        return 10


def score_credit_gap(avg_credit_score: float) -> float:
    """
    Score based on average credit score.
    Lower credit = more underserved.

    Thresholds:
    - <600: Severely underserved
    - 600-649: Underserved
    - 650-679: At-risk
    - 680+: Stable
    """
    if avg_credit_score < 580:
        return 100
    elif avg_credit_score < 620:
        return 80
    elif avg_credit_score < 650:
        return 60
    elif avg_credit_score < 680:
        return 40
    elif avg_credit_score < 720:
        return 20
    else:
        return 5


def score_minority_share(pct_minority: float) -> float:
    """
    Score based on minority population share.
    Higher minority % correlated with underserved status.

    Note: This is a statistical correlation, not causation.
    """
    if pct_minority >= 90:
        return 100
    elif pct_minority >= 75:
        return 75
    elif pct_minority >= 60:
        return 50
    elif pct_minority >= 50:
        return 30
    else:
        return 10


# ==================== Underserved Index Calculation ====================

def calculate_underserved_index(
    demographics: DemographicProfile,
    economics: EconomicProfile,
    housing: HousingProfile,
    credit: CreditProfile,
    mortgage_market: MortgageMarketProfile
) -> float:
    """
    Calculate overall Underserved Index (0-100).

    Weighted average of multiple factors:
    - Homeownership gap (25%)
    - Rent burden (20%)
    - Mortgage denial rate (20%)
    - AMI gap (15%)
    - Credit gap (10%)
    - Minority share (10%)
    """

    # Calculate component scores
    homeowner_score = score_homeownership(housing.homeownership_rate)
    rent_burden_score = score_rent_burden(housing.severe_rent_burden_rate)
    denial_score = score_denial_rate(mortgage_market.denial_rate)
    ami_score = score_ami_gap(economics.ami_ratio)
    credit_score = score_credit_gap(credit.avg_credit_score)
    minority_score = score_minority_share(demographics.pct_minority)

    # Weighted average
    index = (
        homeowner_score * 0.25 +
        rent_burden_score * 0.20 +
        denial_score * 0.20 +
        ami_score * 0.15 +
        credit_score * 0.10 +
        minority_score * 0.10
    )

    return round(index, 2)


def classify_underserved_level(index: float) -> str:
    """Classify underserved level based on index score."""
    if index >= 80:
        return "Severely Underserved"
    elif index >= 60:
        return "Underserved"
    elif index >= 40:
        return "At-Risk"
    else:
        return "Stable/Upward Mobility"


# ==================== Signal Detection ====================

def detect_underserved_signals(
    demographics: DemographicProfile,
    economics: EconomicProfile,
    housing: HousingProfile,
    credit: CreditProfile,
    mortgage_market: MortgageMarketProfile
) -> UnderservedSignals:
    """
    Detect specific underserved signals.
    Returns binary flags for each signal.
    """

    # Detect individual signals
    low_homeownership = housing.homeownership_rate < 45.0
    high_rent_burden = housing.severe_rent_burden_rate > 30.0
    high_denial_rate = mortgage_market.denial_rate > 25.0
    low_ami_ratio = economics.ami_ratio < 0.80
    majority_minority = demographics.pct_minority > 50.0
    persistent_poverty = economics.poverty_rate > 20.0
    low_credit_cluster = credit.avg_credit_score < 680
    high_fthb_demand = mortgage_market.estimated_fthb_rate > 40.0
    high_foreclosure_rate = credit.foreclosure_rate > 5.0

    # Count signals
    signals = [
        low_homeownership,
        high_rent_burden,
        high_denial_rate,
        low_ami_ratio,
        majority_minority,
        persistent_poverty,
        low_credit_cluster,
        high_fthb_demand,
        high_foreclosure_rate
    ]
    signal_count = sum(signals)

    # Determine severity
    if signal_count >= 7:
        severity = "Severe"
    elif signal_count >= 5:
        severity = "High"
    elif signal_count >= 3:
        severity = "Moderate"
    else:
        severity = "Low"

    return UnderservedSignals(
        low_homeownership=low_homeownership,
        high_rent_burden=high_rent_burden,
        high_denial_rate=high_denial_rate,
        low_ami_ratio=low_ami_ratio,
        majority_minority=majority_minority,
        persistent_poverty=persistent_poverty,
        low_credit_cluster=low_credit_cluster,
        high_fthb_demand=high_fthb_demand,
        high_foreclosure_rate=high_foreclosure_rate,
        signal_count=signal_count,
        severity_level=severity
    )


# ==================== Key Insights Generation ====================

def generate_key_challenges(
    signals: UnderservedSignals,
    economics: EconomicProfile,
    housing: HousingProfile,
    credit: CreditProfile,
    mortgage_market: MortgageMarketProfile
) -> list[str]:
    """Generate list of key challenges facing the community."""
    challenges = []

    if signals.low_homeownership:
        challenges.append(
            f"Very low homeownership rate ({housing.homeownership_rate:.1f}%) - "
            f"community wealth-building constrained"
        )

    if signals.high_rent_burden:
        challenges.append(
            f"Severe rent burden ({housing.severe_rent_burden_rate:.1f}% paying >50% of income) - "
            f"difficult to save for down payment"
        )

    if signals.high_denial_rate:
        challenges.append(
            f"High mortgage denial rate ({mortgage_market.denial_rate:.1f}%) - "
            f"access to credit severely limited"
        )

    if signals.low_ami_ratio:
        challenges.append(
            f"Income well below area median ({economics.ami_ratio:.1%} of AMI) - "
            f"affordability crisis"
        )

    if signals.low_credit_cluster:
        challenges.append(
            f"Low average credit score ({credit.avg_credit_score:.0f}) - "
            f"conventional lending difficult"
        )

    if signals.persistent_poverty:
        challenges.append(
            f"High poverty rate ({economics.poverty_rate:.1f}%) - "
            f"economic instability"
        )

    if signals.high_foreclosure_rate:
        challenges.append(
            f"Elevated foreclosure rate ({credit.foreclosure_rate:.1f} per 1000) - "
            f"housing instability"
        )

    if credit.pct_high_dti > 40:
        challenges.append(
            f"High debt-to-income burdens ({credit.avg_dti_ratio:.1f}% avg DTI) - "
            f"limited borrowing capacity"
        )

    return challenges


def generate_key_opportunities(
    signals: UnderservedSignals,
    housing: HousingProfile,
    mortgage_market: MortgageMarketProfile,
    demographics: DemographicProfile
) -> list[str]:
    """Generate list of key opportunities for the community."""
    opportunities = []

    if signals.high_fthb_demand:
        opportunities.append(
            f"High first-time buyer demand ({mortgage_market.estimated_fthb_rate:.1f}%) - "
            f"FTHB programs with LTV waivers highly relevant"
        )

    if housing.median_home_value < 250_000:
        opportunities.append(
            f"Affordable home prices (median ${housing.median_home_value:,.0f}) - "
            f"lower loan amounts reduce risk"
        )

    if signals.low_ami_ratio:
        opportunities.append(
            "Income-qualified for HomeReady/Home Possible with LLPA waivers - "
            "significant pricing advantages available"
        )

    if housing.pct_2_4_units > 20:
        opportunities.append(
            f"Multi-unit housing stock ({housing.pct_2_4_units:.0f}% 2-4 units) - "
            f"rental income can support qualification"
        )

    if mortgage_market.pct_fha > 50:
        opportunities.append(
            f"FHA market-ready ({mortgage_market.pct_fha:.0f}% FHA loans) - "
            f"infrastructure exists for government lending"
        )

    if demographics.total_population > 50_000:
        opportunities.append(
            f"Large population base ({demographics.total_population:,}) - "
            f"scale opportunity for community lending"
        )

    if housing.is_high_cost_area:
        opportunities.append(
            "High-balance loan limits available - "
            "supports higher loan amounts for expensive markets"
        )

    opportunities.append(
        "Community-focused lending with tailored education can dramatically improve outcomes"
    )

    return opportunities
