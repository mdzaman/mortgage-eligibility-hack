"""
Community Outreach Letter Generator

Generates personalized outreach letters for underserved communities
based on community analysis results.
"""

from typing import Optional
from datetime import datetime
from models_community import CommunityInsightResult, CommunityProfile, BorrowerPersona


def generate_community_letter(
    result: CommunityInsightResult,
    lender_name: str = "Your Local Mortgage Lender",
    loan_officer_name: str = "Community Lending Team",
    phone: str = "(555) 123-4567",
    email: str = "community@lender.com",
    letter_type: str = "introduction"
) -> str:
    """
    Generate a community outreach letter.

    Args:
        result: CommunityInsightResult from analysis
        lender_name: Name of lending institution
        loan_officer_name: Name of loan officer or team
        phone: Contact phone number
        email: Contact email
        letter_type: Type of letter ('introduction', 'workshop', 'partnership')

    Returns:
        Formatted letter as string
    """

    if letter_type == "introduction":
        return _generate_introduction_letter(
            result, lender_name, loan_officer_name, phone, email
        )
    elif letter_type == "workshop":
        return _generate_workshop_invitation(
            result, lender_name, loan_officer_name, phone, email
        )
    elif letter_type == "partnership":
        return _generate_partnership_letter(
            result, lender_name, loan_officer_name, phone, email
        )
    else:
        raise ValueError(f"Unknown letter type: {letter_type}")


def _generate_introduction_letter(
    result: CommunityInsightResult,
    lender_name: str,
    loan_officer_name: str,
    phone: str,
    email: str
) -> str:
    """Generate introduction letter to community."""

    profile = result.community_profile
    persona = result.borrower_persona
    optimal_program = result.mortgage_recommendation.optimal_program

    date = datetime.now().strftime("%B %d, %Y")

    # Format statistics
    homeownership_rate = f"{profile.housing.homeownership_rate:.1f}%"
    median_income = f"${profile.economics.median_household_income:,.0f}"
    target_price = f"${persona.target_home_price:,.0f}"
    down_payment = f"{persona.typical_down_payment_pct:.1f}%"

    # Language support
    languages = ", ".join(result.quick_serve_plan.multilingual_staff_needed)

    letter = f"""
{lender_name}
Community Lending Division
{date}

Dear {profile.name} Community Members,

RE: Expanding Homeownership Opportunities in {profile.name}

We are reaching out to introduce specialized mortgage services designed specifically for families in {profile.name}. Our analysis shows that your community has a homeownership rate of {homeownership_rate}, which is below the regional average, and we believe we can help more families achieve the dream of homeownership.

**Understanding Your Community's Needs**

Based on our research, we understand that:
• Median household income in {profile.name} is {median_income}
• Many families are seeking homes in the {target_price} range
• Down payment savings can be a challenge, with many families able to put down {down_payment}
• Credit building support may be helpful for some applicants
• {languages} language services are important to serve the community

**How We Can Help**

We offer several mortgage programs that are well-suited for {profile.name} residents:

1. **{optimal_program.program.value}** (Recommended)
   • Down payment as low as {optimal_program.max_ltv:.1f}% LTV (only {100 - optimal_program.max_ltv:.1f}% down)
   • Credit scores starting at {optimal_program.min_credit_score}
   • Estimated rates: {optimal_program.estimated_rate_range[0]:.3f}% - {optimal_program.estimated_rate_range[1]:.3f}%
   • First-time homebuyer programs available
   • Down payment assistance integration

2. **Special Features for Your Community**
   • Free homebuyer education workshops
   • Bilingual services ({languages})
   • Credit improvement guidance
   • Fast-track pre-qualification (3-5 days)
   • Dedicated loan officers who understand your community

**Down Payment Assistance**

We work with multiple down payment assistance programs that can help:
{_format_dpa_programs(result.quick_serve_plan.dpa_integration.available_programs[:3])}

These programs can provide thousands of dollars to help with down payment and closing costs.

**Free Homebuyer Education Workshop**

We invite you to attend our FREE homebuyer education workshop specifically for {profile.name} residents:

What You'll Learn:
• The home buying process from start to finish
• How to improve your credit score
• Understanding mortgage programs and rates
• Down payment assistance options
• Budgeting for homeownership
• Avoiding predatory lending

Workshop Details:
• HUD-approved 8-hour course
• Available in {languages}
• Certificate provided upon completion
• Refreshments provided

**Next Steps**

We make it easy to get started:

1. **Free Consultation** - Call or email us for a no-obligation discussion
2. **Pre-Qualification** - Get pre-qualified in 3-5 days
3. **Find Your Home** - Work with our partner realtors who know {profile.name}
4. **Close on Your Home** - Typical timeline: 30-45 days

**Our Commitment to {profile.name}**

We are committed to serving your community with:
✓ Transparent pricing - no hidden fees
✓ Education-first approach
✓ Cultural sensitivity and respect
✓ Partnership with trusted local organizations
✓ Long-term community investment

**Contact Us Today**

{loan_officer_name}
{lender_name}
Phone: {phone}
Email: {email}

Office Hours: Monday-Friday 9am-6pm, Saturday 10am-2pm
Evening appointments available by request

We look forward to helping you achieve homeownership!

Sincerely,

{loan_officer_name}
Community Lending Specialist
{lender_name}

---

P.S. Ask about our current special offer: Free credit report review and improvement plan for all {profile.name} residents who schedule a consultation this month!

---

**Important Information:**

This letter is for informational purposes only and does not constitute a commitment to lend. All loans subject to credit approval. Rates and programs subject to change. Equal Housing Opportunity Lender. Licensed by [State Department of Financial Services].

Analysis based on community data as of {result.analysis_timestamp[:10]}. Individual circumstances may vary. We encourage all interested homebuyers to schedule a consultation to discuss their specific situation.
"""

    return letter.strip()


def _generate_workshop_invitation(
    result: CommunityInsightResult,
    lender_name: str,
    loan_officer_name: str,
    phone: str,
    email: str
) -> str:
    """Generate workshop invitation letter."""

    profile = result.community_profile
    date = datetime.now().strftime("%B %d, %Y")

    languages = ", ".join(result.quick_serve_plan.multilingual_staff_needed)

    letter = f"""
{lender_name}
Community Education Program
{date}

FREE HOMEBUYER EDUCATION WORKSHOP
{profile.name} Community

Dear Community Member,

You are invited to attend a FREE Homebuyer Education Workshop designed specifically for {profile.name} residents!

**Workshop Details:**

📅 Date: [To Be Scheduled - Multiple Sessions Available]
🕐 Time: Saturday 9:00 AM - 5:00 PM (includes lunch)
📍 Location: [Local Community Center - TBD]
💰 Cost: FREE (includes materials, lunch, and certificate)
🗣️ Languages: {languages}

**What You'll Learn:**

✓ Understanding Your Home Buying Power
  • Calculate what you can afford
  • Understanding credit scores and how to improve them
  • Building savings for down payment

✓ The Home Buying Process
  • Finding the right home and neighborhood
  • Working with real estate agents
  • Making an offer and negotiating

✓ Mortgage Programs That Work for You
  • FHA, Conventional, and special programs
  • Down payment assistance (thousands of $$ available!)
  • Understanding rates and closing costs

✓ Protecting Your Investment
  • Home inspections and appraisals
  • Insurance requirements
  • Avoiding foreclosure and predatory lending

✓ Long-term Success
  • Budgeting for homeownership
  • Maintenance and repairs
  • Building equity and wealth

**Why Attend?**

• HUD-Approved Certification - Required for some down payment assistance programs
• Expert Instructors - Experienced mortgage professionals
• Community-Focused - Examples relevant to {profile.name}
• Ask Questions - Small group setting, lots of interaction
• Free Resources - Take home guides and checklists
• Networking - Meet other aspiring homeowners from your community

**Special Benefits for Workshop Attendees:**

🎁 Free credit report review (save $50)
🎁 Priority pre-qualification processing
🎁 Access to exclusive down payment assistance programs
🎁 Discounted home inspection services

**Current Market Conditions in {profile.name}:**

• Median home price: ${profile.housing.median_home_value:,.0f}
• Average down payment needed: ${result.borrower_persona.typical_down_payment_amount:,.0f}
• Down payment assistance available: ${result.quick_serve_plan.dpa_integration.typical_assistance_amount:,.0f}
• Your estimated monthly payment: ${_estimate_payment(result.borrower_persona):,.0f}

**Registration Required - Limited Space!**

To register, contact us:
📞 Phone: {phone}
✉️ Email: {email}

Or visit our office:
[Office Address - TBD]

**About Our Program:**

{lender_name} is committed to expanding homeownership opportunities in {profile.name}. This workshop is part of our community investment initiative to help more families achieve the American Dream of homeownership.

We look forward to seeing you at the workshop!

Sincerely,

{loan_officer_name}
Community Education Coordinator
{lender_name}

---

P.S. Bring your questions! Our instructors are here to help YOU succeed.

---
Equal Housing Opportunity. This workshop is provided free as a community service. No obligation to apply for a mortgage. All attendees welcome regardless of where they choose to obtain financing.
"""

    return letter.strip()


def _generate_partnership_letter(
    result: CommunityInsightResult,
    lender_name: str,
    loan_officer_name: str,
    phone: str,
    email: str
) -> str:
    """Generate partnership proposal letter for community organizations."""

    profile = result.community_profile
    date = datetime.now().strftime("%B %d, %Y")

    target_volume = result.quick_serve_plan.target_volume_per_month * 12

    letter = f"""
{lender_name}
Community Partnership Program
{date}

RE: Partnership Opportunity - Expanding Homeownership in {profile.name}

Dear Community Organization Leader,

I am writing to explore a partnership opportunity between {lender_name} and your organization to expand homeownership opportunities for families in {profile.name}.

**The Opportunity**

Our analysis shows that {profile.name} is an underserved community with significant homeownership potential:

• Current homeownership rate: {profile.housing.homeownership_rate:.1f}%
• Estimated annual mortgage demand: {profile.mortgage_market.total_applications:,.0f} applications
• Our target: Help {target_volume} families annually achieve homeownership

We believe that by working together, we can make a meaningful impact in your community.

**Why Partnership?**

Your organization has the trust of the community. We have the mortgage expertise and resources. Together, we can:

✓ Provide financial education workshops at your facilities
✓ Offer free credit counseling and improvement programs
✓ Connect families with down payment assistance (${result.quick_serve_plan.dpa_integration.typical_assistance_amount:,.0f} average)
✓ Create fast-track mortgage processing for your members
✓ Provide bilingual services in {", ".join(result.quick_serve_plan.multilingual_staff_needed)}

**What We Offer Partners:**

1. **Free Educational Workshops**
   • HUD-approved homebuyer education
   • Credit building seminars
   • Financial literacy classes
   • All at no cost to your organization or members

2. **Dedicated Support**
   • Assigned loan officer for your organization
   • Priority processing for referrals
   • Regular office hours at your location
   • Bilingual staff available

3. **Marketing Support**
   • Co-branded materials
   • Social media support
   • Success stories and testimonials
   • Community event participation

4. **Transparent Process**
   • No hidden fees
   • Clear communication
   • Regular reporting on outcomes
   • Feedback and improvement

**Partnership Models**

We offer flexible partnership arrangements:

**Option 1: Educational Partner**
• We provide workshops at your facility
• You promote to your members
• No financial commitment required

**Option 2: Referral Partner**
• You refer interested homebuyers
• We provide dedicated service
• Track outcomes together

**Option 3: Strategic Partner**
• Comprehensive collaboration
• Joint community events
• Co-develop programs
• Long-term commitment

**Our Track Record**

{lender_name} has partnered with [X] community organizations and helped [Y] families achieve homeownership in the past [Z] years. We are committed to:

• Fair Lending - Equal opportunity for all applicants
• Community Investment - CRA credits demonstrate our commitment
• Sustainability - Education-first approach prevents foreclosures
• Transparency - Clear terms and honest advice

**Community Impact Potential**

If we reach our goal of {target_volume} mortgages annually in {profile.name}:

• ${target_volume * result.borrower_persona.target_home_price:,.0f} in community investment
• {target_volume} families building wealth through homeownership
• Strengthened neighborhood stability
• Economic development through increased homeownership

**Next Steps**

I would welcome the opportunity to meet with you to discuss this partnership in more detail. I am available at your convenience and happy to visit your office.

Specifically, I'd like to discuss:
1. Your organization's goals and priorities
2. How we can best serve your members
3. Logistics of educational workshops
4. Success metrics and reporting
5. Timeline for launch

**Contact Information**

{loan_officer_name}
Community Partnership Director
{lender_name}

Phone: {phone}
Email: {email}
Office: [Address - TBD]

**References Available**

We are happy to provide references from other community organizations we have partnered with, as well as testimonials from families we have helped.

I look forward to exploring how we can work together to expand homeownership opportunities in {profile.name}.

Sincerely,

{loan_officer_name}
Community Partnership Director
{lender_name}

---

**Attachments:**
• {lender_name} Community Impact Report
• Partnership Program Overview
• Sample Workshop Agenda
• Success Stories

---

{lender_name} is an Equal Housing Opportunity Lender. We are committed to fair lending practices and compliance with all applicable laws and regulations. Licensed by [State Department of Financial Services].
"""

    return letter.strip()


def _format_dpa_programs(programs: list) -> str:
    """Format DPA programs as bullet list."""
    if not programs:
        return "   • Contact us for available programs"

    formatted = []
    for i, program in enumerate(programs, 1):
        formatted.append(f"   • {program}")
    return "\n".join(formatted)


def _estimate_payment(persona: BorrowerPersona) -> float:
    """Estimate monthly payment for persona."""
    # Simple estimation: P&I + taxes + insurance + MI
    loan_amount = persona.target_loan_amount
    rate = 0.0675  # 6.75% estimate
    term = 360

    # Monthly P&I
    monthly_rate = rate / 12
    pi = loan_amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)

    # Add estimates for taxes, insurance, MI
    taxes = (persona.target_home_price * 0.012) / 12  # 1.2% annual
    insurance = (persona.target_home_price * 0.005) / 12  # 0.5% annual
    mi = 0
    if persona.typical_down_payment_pct < 20:
        mi = loan_amount * 0.005 / 12  # 0.5% MI

    return pi + taxes + insurance + mi


def generate_all_letters(
    result: CommunityInsightResult,
    lender_name: str = "Your Local Mortgage Lender",
    loan_officer_name: str = "Community Lending Team",
    phone: str = "(555) 123-4567",
    email: str = "community@lender.com"
) -> dict:
    """
    Generate all letter types for a community.

    Returns:
        Dictionary with letter types as keys and letter text as values
    """
    return {
        "introduction": generate_community_letter(
            result, lender_name, loan_officer_name, phone, email, "introduction"
        ),
        "workshop": generate_community_letter(
            result, lender_name, loan_officer_name, phone, email, "workshop"
        ),
        "partnership": generate_community_letter(
            result, lender_name, loan_officer_name, phone, email, "partnership"
        )
    }


def save_letter_to_file(letter: str, filename: str):
    """Save letter to text file."""
    with open(filename, 'w') as f:
        f.write(letter)
    print(f"Letter saved to: {filename}")
