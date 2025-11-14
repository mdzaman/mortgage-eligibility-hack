"""
Example: Generate Community Outreach Letters

This script demonstrates how to generate personalized outreach letters
for underserved communities using the CommunityInsightEngine.
"""

from community_engine import CommunityInsightEngine
from models_community import GeographyInput
from community_letter_generator import (
    generate_community_letter,
    generate_all_letters,
    save_letter_to_file
)


def generate_harlem_letters():
    """Generate all letters for Harlem community."""
    print("\n" + "=" * 80)
    print("GENERATING LETTERS FOR HARLEM (10026)")
    print("=" * 80)

    # Analyze community
    engine = CommunityInsightEngine()
    geography = GeographyInput(
        state="NY",
        county="New York County",
        city="New York",
        borough="Manhattan",
        zip_code="10026"
    )

    result = engine.analyze_community(geography)

    # Lender information (customize this)
    lender_name = "Community First Mortgage"
    loan_officer_name = "Maria Rodriguez"
    phone = "(212) 555-1234"
    email = "maria.rodriguez@communityfirstmtg.com"

    # Generate all letter types
    letters = generate_all_letters(
        result,
        lender_name=lender_name,
        loan_officer_name=loan_officer_name,
        phone=phone,
        email=email
    )

    # Save letters to files
    for letter_type, letter_text in letters.items():
        filename = f"letter_harlem_{letter_type}.txt"
        save_letter_to_file(letter_text, filename)
        print(f"✓ Generated {letter_type} letter")

    # Print preview of introduction letter
    print("\n" + "=" * 80)
    print("PREVIEW: INTRODUCTION LETTER (First 50 lines)")
    print("=" * 80)
    lines = letters["introduction"].split("\n")
    print("\n".join(lines[:50]))
    print(f"\n... ({len(lines)} total lines)")


def generate_south_bronx_letters():
    """Generate all letters for South Bronx community."""
    print("\n" + "=" * 80)
    print("GENERATING LETTERS FOR SOUTH BRONX (10453)")
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

    # Customize for Spanish-speaking community
    lender_name = "Community First Mortgage"
    loan_officer_name = "Carlos Mendez"
    phone = "(718) 555-5678"
    email = "carlos.mendez@communityfirstmtg.com"

    # Generate workshop invitation (most relevant for high FTHB rate)
    workshop_letter = generate_community_letter(
        result,
        lender_name=lender_name,
        loan_officer_name=loan_officer_name,
        phone=phone,
        email=email,
        letter_type="workshop"
    )

    save_letter_to_file(workshop_letter, "letter_south_bronx_workshop.txt")
    print("✓ Generated workshop invitation letter")


def generate_partnership_proposal():
    """Generate partnership letter for Buffalo community organization."""
    print("\n" + "=" * 80)
    print("GENERATING PARTNERSHIP LETTER FOR BUFFALO (14211)")
    print("=" * 80)

    engine = CommunityInsightEngine()
    geography = GeographyInput(
        state="NY",
        county="Erie County",
        city="Buffalo",
        zip_code="14211"
    )

    result = engine.analyze_community(geography)

    lender_name = "Western New York Community Lending"
    loan_officer_name = "Jennifer Williams"
    phone = "(716) 555-9012"
    email = "j.williams@wnycl.com"

    partnership_letter = generate_community_letter(
        result,
        lender_name=lender_name,
        loan_officer_name=loan_officer_name,
        phone=phone,
        email=email,
        letter_type="partnership"
    )

    save_letter_to_file(partnership_letter, "letter_buffalo_partnership.txt")
    print("✓ Generated partnership proposal letter")

    # Print preview
    print("\n" + "=" * 80)
    print("PREVIEW: PARTNERSHIP LETTER (First 40 lines)")
    print("=" * 80)
    lines = partnership_letter.split("\n")
    print("\n".join(lines[:40]))
    print(f"\n... ({len(lines)} total lines)")


def generate_custom_letter():
    """Example of generating a custom letter with specific parameters."""
    print("\n" + "=" * 80)
    print("GENERATING CUSTOM LETTER FOR JAMAICA, QUEENS (11432)")
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

    # Custom lender info
    lender_name = "Queens Community Bank"
    loan_officer_name = "Raj Patel"
    phone = "(718) 555-3456"
    email = "rpatel@queenscommunitybank.com"

    # Generate introduction letter
    intro_letter = generate_community_letter(
        result,
        lender_name=lender_name,
        loan_officer_name=loan_officer_name,
        phone=phone,
        email=email,
        letter_type="introduction"
    )

    save_letter_to_file(intro_letter, "letter_jamaica_queens_intro.txt")
    print("✓ Generated custom introduction letter")

    # Show key statistics from the letter
    print("\nKEY COMMUNITY STATISTICS:")
    print(f"  • Community: {result.community_profile.name}")
    print(f"  • Homeownership Rate: {result.community_profile.housing.homeownership_rate:.1f}%")
    print(f"  • Median Income: ${result.community_profile.economics.median_household_income:,.0f}")
    print(f"  • Underserved Index: {result.community_profile.underserved_index:.1f}")
    print(f"  • Optimal Program: {result.mortgage_recommendation.optimal_program.program.value}")
    print(f"  • Languages Needed: {', '.join(result.quick_serve_plan.multilingual_staff_needed)}")


def compare_letter_approaches():
    """Compare different letter types for the same community."""
    print("\n" + "=" * 80)
    print("COMPARING LETTER TYPES FOR SAME COMMUNITY")
    print("=" * 80)

    engine = CommunityInsightEngine()
    geography = GeographyInput(
        state="NY",
        zip_code="10026"  # Harlem
    )

    result = engine.analyze_community(geography)

    lender_name = "Test Lender"
    loan_officer_name = "Test Officer"
    phone = "(555) 000-0000"
    email = "test@test.com"

    letters = generate_all_letters(
        result, lender_name, loan_officer_name, phone, email
    )

    print("\nLETTER LENGTH COMPARISON:")
    for letter_type, letter_text in letters.items():
        lines = len(letter_text.split("\n"))
        chars = len(letter_text)
        words = len(letter_text.split())
        print(f"\n  {letter_type.upper()}:")
        print(f"    • Lines: {lines}")
        print(f"    • Words: {words:,}")
        print(f"    • Characters: {chars:,}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "COMMUNITY LETTER GENERATOR EXAMPLES" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")

    # Generate letters for different communities
    generate_harlem_letters()
    generate_south_bronx_letters()
    generate_partnership_proposal()
    generate_custom_letter()

    # Compare approaches
    compare_letter_approaches()

    print("\n" + "=" * 80)
    print("LETTER GENERATION COMPLETE")
    print("=" * 80)
    print("\nGENERATED FILES:")
    print("  • letter_harlem_introduction.txt")
    print("  • letter_harlem_workshop.txt")
    print("  • letter_harlem_partnership.txt")
    print("  • letter_south_bronx_workshop.txt")
    print("  • letter_buffalo_partnership.txt")
    print("  • letter_jamaica_queens_intro.txt")

    print("\nNEXT STEPS:")
    print("  1. Review generated letters and customize as needed")
    print("  2. Add your actual lender information")
    print("  3. Print on letterhead for mailing")
    print("  4. Convert to email templates for digital outreach")
    print("  5. Translate to Spanish/other languages as needed")
    print("  6. Track response rates by letter type and community")
    print("")


if __name__ == "__main__":
    main()
