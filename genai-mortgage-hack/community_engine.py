"""
Community Insight Engine - Main Orchestrator

This is the main entry point for community mortgage intelligence analysis.
It orchestrates all components to provide complete community insights.

Usage:
    from community_engine import CommunityInsightEngine
    from models_community import GeographyInput

    engine = CommunityInsightEngine()
    result = engine.analyze_community(GeographyInput(
        state="NY",
        zip_code="10026"
    ))
"""

from typing import List, Dict, Optional
from datetime import datetime

# Import models
from models_community import (
    GeographyInput, CommunityProfile, CommunityInsightResult,
    CommunityPricingRecommendation, BorrowerPersona, QuickServePlan
)

# Import data loader
from community_data_loader import (
    get_community_data, get_available_communities,
    load_demographics, load_economics, load_housing,
    load_credit, load_mortgage_market
)

# Import rules engine
from community_rules import (
    calculate_underserved_index, classify_underserved_level,
    detect_underserved_signals, generate_key_challenges,
    generate_key_opportunities
)

# Import persona generator
from community_profiles import (
    generate_borrower_persona, generate_scenario_dict
)

# Import recommendations engine
from community_recommendations import (
    generate_mortgage_recommendation, create_quick_serve_plan
)


class CommunityInsightEngine:
    """
    Main engine for community mortgage intelligence analysis.

    Identifies underserved communities, generates borrower personas,
    and produces tailored mortgage recommendations.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Community Insight Engine.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.version = "1.0.0"

    def analyze_community(self, geography: GeographyInput) -> CommunityInsightResult:
        """
        Perform complete community analysis.

        This is the main method that orchestrates all components:
        1. Load community data
        2. Calculate underserved index
        3. Generate borrower persona
        4. Generate mortgage recommendations
        5. Price typical scenario
        6. Create quick-serve plan

        Args:
            geography: Geographic location to analyze

        Returns:
            Complete CommunityInsightResult

        Raises:
            ValueError: If community data not found
        """
        # Step 1: Load community data
        if not geography.zip_code:
            raise ValueError("ZIP code required for community analysis")

        raw_data = get_community_data(geography.zip_code)
        if not raw_data:
            raise ValueError(f"No data available for ZIP code {geography.zip_code}")

        # Step 2: Build community profile components
        demographics = load_demographics(raw_data)
        economics = load_economics(raw_data)
        housing = load_housing(raw_data, raw_data["county"])
        credit = load_credit(raw_data)
        mortgage_market = load_mortgage_market(raw_data)

        # Step 3: Calculate underserved metrics
        underserved_index = calculate_underserved_index(
            demographics, economics, housing, credit, mortgage_market
        )

        underserved_classification = classify_underserved_level(underserved_index)

        underserved_signals = detect_underserved_signals(
            demographics, economics, housing, credit, mortgage_market
        )

        # Step 4: Generate insights
        key_challenges = generate_key_challenges(
            underserved_signals, economics, housing, credit, mortgage_market
        )

        key_opportunities = generate_key_opportunities(
            underserved_signals, housing, mortgage_market, demographics
        )

        # Step 5: Assemble complete community profile
        community_profile = CommunityProfile(
            geography=geography,
            name=raw_data["name"],
            demographics=demographics,
            economics=economics,
            housing=housing,
            credit=credit,
            mortgage_market=mortgage_market,
            underserved_signals=underserved_signals,
            underserved_index=underserved_index,
            underserved_classification=underserved_classification,
            key_challenges=key_challenges,
            key_opportunities=key_opportunities
        )

        # Step 6: Generate borrower persona
        borrower_persona = generate_borrower_persona(community_profile)

        # Step 7: Generate mortgage recommendations
        mortgage_recommendation = generate_mortgage_recommendation(
            community_profile, borrower_persona
        )

        # Step 8: Price typical scenario
        pricing_recommendation = self._generate_pricing(
            borrower_persona, housing
        )

        # Step 9: Create quick-serve plan
        quick_serve_plan = create_quick_serve_plan(
            community_profile,
            borrower_persona,
            mortgage_recommendation.recommended_programs
        )

        # Step 10: Generate executive summary
        executive_summary = self._generate_executive_summary(
            community_profile, borrower_persona, mortgage_recommendation
        )

        # Step 11: Generate action items
        action_items = self._generate_action_items(
            community_profile, mortgage_recommendation, quick_serve_plan
        )

        # Step 12: Assemble final result
        result = CommunityInsightResult(
            geography=geography,
            community_profile=community_profile,
            borrower_persona=borrower_persona,
            mortgage_recommendation=mortgage_recommendation,
            pricing_recommendation=pricing_recommendation,
            quick_serve_plan=quick_serve_plan,
            executive_summary=executive_summary,
            action_items=action_items,
            analysis_timestamp=datetime.now().isoformat(),
            data_sources=[
                "US Census Bureau (simulated)",
                "HUD AMI Data (simulated)",
                "FHFA Loan Limits",
                "CFPB HMDA (simulated)",
                "Credit Bureau Aggregates (simulated)"
            ],
            confidence_score=85.0  # Based on data quality
        )

        return result

    def _generate_pricing(self, persona: BorrowerPersona,
                         housing) -> CommunityPricingRecommendation:
        """
        Generate pricing recommendation for typical scenario.

        Note: This uses simulated pricing. In production, this would
        call the actual 16-rule mortgage pricing engine.
        """
        # Generate scenario dict
        scenario_dict = generate_scenario_dict(persona, housing)

        # Calculate basic metrics
        ltv = (persona.target_loan_amount / persona.target_home_price) * 100
        dti = (persona.typical_debt_amount / (persona.income_range[0] / 12)) * 100

        # Simulate eligibility (in production, call price_scenario())
        eligibility = True
        if persona.typical_credit_score < 580:
            eligibility = False
        if ltv > 97:
            eligibility = False
        if dti > 50:
            eligibility = False

        # Simulate pricing
        base_rate = 6.50
        base_price = 101.00

        # Simplified LLPA calculation
        llpa_components = []

        # Credit/LTV adjustment
        if persona.typical_credit_score < 680:
            llpa_components.append({
                "name": "Credit_LTV_Adjustment",
                "value_bps": 1.50,
                "reason": f"Credit {persona.typical_credit_score}, LTV {ltv:.1f}%"
            })
        else:
            llpa_components.append({
                "name": "Credit_LTV_Adjustment",
                "value_bps": 0.25,
                "reason": f"Credit {persona.typical_credit_score}, LTV {ltv:.1f}%"
            })

        # FTHB waiver
        waivers = []
        if persona.likely_first_time_buyer:
            llpa_components.append({
                "name": "FTHB_Waiver",
                "value_bps": -0.50,
                "reason": "First-time homebuyer adjustment"
            })
            waivers.append("First-Time Homebuyer")

        llpa_total = sum(c["value_bps"] for c in llpa_components)
        net_price = base_price - (llpa_total / 100)

        # Potential improvements
        improvements = []
        if persona.typical_credit_score < 720:
            target_score = 720
            savings = 0.50
            improvements.append(
                f"Improve credit score to {target_score} could save ~{savings:.2f}% ({savings * 100:.0f} bps)"
            )

        if ltv > 90 and persona.needs_dpa:
            improvements.append(
                "Additional down payment to reduce LTV below 90% could save 0.25-0.50%"
            )

        estimated_savings = sum([0.50 if "credit" in imp.lower() else 0.25 for imp in improvements])

        return CommunityPricingRecommendation(
            base_scenario=scenario_dict,
            eligibility_overall=eligibility,
            calculated_ltv=ltv,
            calculated_dti=dti,
            base_rate=base_rate,
            base_price=base_price,
            llpa_total_bps=llpa_total,
            net_price=net_price,
            llpa_components=llpa_components,
            waivers_applied=waivers,
            potential_improvements=improvements,
            estimated_savings_bps=estimated_savings * 100
        )

    def _generate_executive_summary(self, profile: CommunityProfile,
                                    persona: BorrowerPersona,
                                    recommendation) -> str:
        """Generate executive summary of analysis."""
        summary = f"""
COMMUNITY MORTGAGE INTELLIGENCE REPORT
{profile.name}

UNDERSERVED STATUS: {profile.underserved_classification}
Underserved Index: {profile.underserved_index:.1f}/100

KEY METRICS:
• Homeownership Rate: {profile.housing.homeownership_rate:.1f}%
• Median Income: ${profile.economics.median_household_income:,.0f} ({profile.economics.ami_ratio:.1%} of AMI)
• Average Credit Score: {profile.credit.avg_credit_score:.0f}
• Mortgage Denial Rate: {profile.mortgage_market.denial_rate:.1f}%
• First-Time Buyer Estimate: {profile.mortgage_market.estimated_fthb_rate:.1f}%

TYPICAL HOMEBUYER PROFILE:
• {persona.persona_name}
• Income: ${persona.income_range[0]:,.0f} - ${persona.income_range[1]:,.0f}
• Credit Score: {persona.typical_credit_score}
• Target Home Price: ${persona.target_home_price:,.0f}
• Down Payment: {persona.typical_down_payment_pct:.1f}% (${persona.typical_down_payment_amount:,.0f})

OPTIMAL MORTGAGE PROGRAM: {recommendation.optimal_program.program.value}
• Overall Fit Score: {recommendation.optimal_program.overall_fit:.0f}/100
• Estimated Rate: {recommendation.optimal_program.estimated_rate_range[0]:.3f}% - {recommendation.optimal_program.estimated_rate_range[1]:.3f}%
• Max LTV: {recommendation.optimal_program.max_ltv:.1f}%
• Min Credit: {recommendation.optimal_program.min_credit_score}

TOP CHALLENGES:
{self._format_list(profile.key_challenges[:3])}

TOP OPPORTUNITIES:
{self._format_list(profile.key_opportunities[:3])}

RECOMMENDED ACTION: Implement community-focused lending program with tailored education,
credit support, and down payment assistance integration.
"""
        return summary.strip()

    def _generate_action_items(self, profile: CommunityProfile,
                               recommendation,
                               quick_serve_plan: QuickServePlan) -> List[str]:
        """Generate prioritized action items."""
        actions = []

        # Priority 1: Immediate setup
        actions.append(
            f"Establish {quick_serve_plan.dedicated_loan_officers} dedicated loan officer(s) "
            f"for {profile.name}"
        )

        if quick_serve_plan.multilingual_staff_needed:
            actions.append(
                f"Hire or train multilingual staff: "
                f"{', '.join(quick_serve_plan.multilingual_staff_needed)}"
            )

        # Priority 2: Partnerships
        top_partners = quick_serve_plan.outreach.partnership_opportunities[:2]
        actions.append(
            f"Establish partnerships with: {', '.join(top_partners)}"
        )

        # Priority 3: Education
        if quick_serve_plan.education.homebuyer_education:
            actions.append(
                "Set up monthly homebuyer education workshops in the community"
            )

        # Priority 4: Credit support
        if profile.underserved_signals.low_credit_cluster:
            actions.append(
                "Develop credit repair referral network and alternative credit evaluation process"
            )

        # Priority 5: DPA integration
        if len(quick_serve_plan.dpa_integration.available_programs) > 0:
            actions.append(
                "Integrate with down payment assistance programs: "
                f"{quick_serve_plan.dpa_integration.available_programs[0]}"
            )

        # Priority 6: Marketing
        actions.append(
            "Launch community awareness campaign through trusted local channels"
        )

        # Priority 7: Technology
        actions.append(
            "Implement digital application platform with mobile-first design"
        )

        # Priority 8: Metrics
        actions.append(
            f"Set performance targets: {quick_serve_plan.target_volume_per_month} loans/month, "
            f"{quick_serve_plan.target_approval_rate:.0f}% approval rate"
        )

        return actions

    def _format_list(self, items: List[str], max_items: int = 5) -> str:
        """Format list of items for display."""
        formatted = []
        for i, item in enumerate(items[:max_items], 1):
            formatted.append(f"{i}. {item}")
        return "\n".join(formatted)

    def get_available_communities(self) -> List[Dict]:
        """
        Get list of all available communities in database.

        Returns:
            List of dictionaries with community info
        """
        return get_available_communities()

    def get_underserved_communities(self, min_index: float = 60.0) -> List[CommunityProfile]:
        """
        Get communities with underserved index above threshold.

        Args:
            min_index: Minimum underserved index (0-100)

        Returns:
            List of CommunityProfile objects for underserved communities
        """
        communities = []

        for community_info in self.get_available_communities():
            try:
                geography = GeographyInput(
                    state="NY",
                    county=community_info["county"],
                    city=community_info["city"],
                    zip_code=community_info["zip_code"],
                    borough=community_info.get("borough")
                )

                result = self.analyze_community(geography)

                if result.community_profile.underserved_index >= min_index:
                    communities.append(result.community_profile)

            except Exception as e:
                print(f"Error analyzing {community_info['name']}: {e}")
                continue

        # Sort by underserved index (descending)
        communities.sort(key=lambda c: c.underserved_index, reverse=True)

        return communities


# ==================== Helper Functions ====================

def print_community_report(result: CommunityInsightResult):
    """Print formatted community analysis report."""
    print("=" * 80)
    print(result.executive_summary)
    print("=" * 80)
    print("\nACTION ITEMS:")
    for i, action in enumerate(result.action_items, 1):
        print(f"{i}. {action}")
    print("=" * 80)


def export_to_dict(result: CommunityInsightResult) -> Dict:
    """Export result to dictionary for JSON serialization."""
    return {
        "community_name": result.community_profile.name,
        "underserved_index": result.community_profile.underserved_index,
        "classification": result.community_profile.underserved_classification,
        "key_metrics": {
            "homeownership_rate": result.community_profile.housing.homeownership_rate,
            "median_income": result.community_profile.economics.median_household_income,
            "avg_credit_score": result.community_profile.credit.avg_credit_score,
            "denial_rate": result.community_profile.mortgage_market.denial_rate
        },
        "persona": {
            "name": result.borrower_persona.persona_name,
            "income_range": result.borrower_persona.income_range,
            "credit_score": result.borrower_persona.typical_credit_score,
            "target_price": result.borrower_persona.target_home_price
        },
        "optimal_program": result.mortgage_recommendation.optimal_program.program.value,
        "estimated_rate": result.mortgage_recommendation.optimal_program.estimated_rate_range,
        "action_items": result.action_items,
        "timestamp": result.analysis_timestamp
    }
