"""
Example: Community Insight Engine Usage

This script demonstrates how to use the CommunityInsightEngine
to analyze underserved communities and generate mortgage recommendations.
"""

from community_engine import CommunityInsightEngine, print_community_report, export_to_dict
from models_community import GeographyInput
import json


def analyze_harlem():
    """Analyze Harlem (10026)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: HARLEM (10026) - MANHATTAN")
    print("=" * 80)

    engine = CommunityInsightEngine()

    geography = GeographyInput(
        state="NY",
        county="New York County",
        city="New York",
        borough="Manhattan",
        zip_code="10026"
    )

    result = engine.analyze_community(geography)

    # Print full report
    print_community_report(result)

    # Show key insights
    print("\nKEY INSIGHTS:")
    print(f"• Signals Detected: {result.community_profile.underserved_signals.signal_count}/9")
    print(f"• Severity: {result.community_profile.underserved_signals.severity_level}")
    print(f"• Optimal Program: {result.mortgage_recommendation.optimal_program.program.value}")
    print(f"• Program Fit Score: {result.mortgage_recommendation.optimal_program.overall_fit:.1f}/100")

    # Show all recommended programs
    print("\nALL RECOMMENDED PROGRAMS (ranked):")
    for i, prog in enumerate(result.mortgage_recommendation.recommended_programs, 1):
        print(f"{i}. {prog.program.value} (Fit: {prog.overall_fit:.1f}/100)")

    # Show quick-serve plan summary
    print("\nQUICK-SERVE PLAN SUMMARY:")
    print(f"• Dedicated LOs: {result.quick_serve_plan.dedicated_loan_officers}")
    print(f"• Languages: {', '.join(result.quick_serve_plan.multilingual_staff_needed)}")
    print(f"• Target Volume: {result.quick_serve_plan.target_volume_per_month} loans/month")
    print(f"• Target Approval: {result.quick_serve_plan.target_approval_rate:.0f}%")


def analyze_south_bronx():
    """Analyze South Bronx (10453)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: SOUTH BRONX (10453)")
    print("=" * 80)

    engine = CommunityInsightEngine()

    geography = GeographyInput(
        state="NY",
        county="Bronx County",
        city="New York",
        borough="Bronx",
        zip_code="10453"
    )

    result = engine.analyze_community(geography)
    print_community_report(result)

    # Export to JSON
    data = export_to_dict(result)
    print("\nJSON EXPORT (sample):")
    print(json.dumps(data, indent=2)[:500] + "...")


def analyze_jamaica_queens():
    """Analyze Jamaica, Queens (11432)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: JAMAICA, QUEENS (11432)")
    print("=" * 80)

    engine = CommunityInsightEngine()

    geography = GeographyInput(
        state="NY",
        county="Queens County",
        city="New York",
        borough="Queens",
        zip_code="11432"
    )

    result = engine.analyze_community(geography)
    print_community_report(result)


def analyze_buffalo():
    """Analyze Buffalo East Side (14211)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: BUFFALO EAST SIDE (14211)")
    print("=" * 80)

    engine = CommunityInsightEngine()

    geography = GeographyInput(
        state="NY",
        county="Erie County",
        city="Buffalo",
        zip_code="14211"
    )

    result = engine.analyze_community(geography)
    print_community_report(result)


def compare_communities():
    """Compare all underserved communities"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: COMPARE ALL UNDERSERVED COMMUNITIES (Index >= 60)")
    print("=" * 80)

    engine = CommunityInsightEngine()

    communities = engine.get_underserved_communities(min_index=60.0)

    print(f"\nFound {len(communities)} underserved communities:\n")

    print(f"{'Rank':<6} {'Community':<30} {'Index':<10} {'Classification':<25} {'Homeownership':<15} {'Avg Credit'}")
    print("-" * 110)

    for i, community in enumerate(communities, 1):
        print(
            f"{i:<6} "
            f"{community.name:<30} "
            f"{community.underserved_index:<10.1f} "
            f"{community.underserved_classification:<25} "
            f"{community.housing.homeownership_rate:<15.1f}% "
            f"{community.credit.avg_credit_score:.0f}"
        )


def show_available_communities():
    """Show all available communities"""
    print("\n" + "=" * 80)
    print("AVAILABLE COMMUNITIES IN DATABASE")
    print("=" * 80)

    engine = CommunityInsightEngine()
    communities = engine.get_available_communities()

    print(f"\nTotal: {len(communities)} communities\n")

    for community in communities:
        borough = f" ({community['borough']})" if community.get('borough') else ""
        print(
            f"• {community['name']:<35} "
            f"ZIP: {community['zip_code']:<10} "
            f"{community['city']}{borough}"
        )


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "COMMUNITY INSIGHT ENGINE EXAMPLES" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")

    # Show available communities
    show_available_communities()

    # Run individual analyses
    analyze_harlem()
    analyze_south_bronx()
    analyze_jamaica_queens()
    analyze_buffalo()

    # Compare communities
    compare_communities()

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80)
    print("\nNEXT STEPS:")
    print("1. Review individual community reports")
    print("2. Prioritize communities based on underserved index")
    print("3. Implement quick-serve plans for top communities")
    print("4. Track performance against target metrics")
    print("5. Expand to additional markets\n")


if __name__ == "__main__":
    main()
