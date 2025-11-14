You are a senior architect, data scientist, and mortgage policy strategist.  
Your task is to design and implement a NEW MODULE that plugs into an existing Fannie Mae–aligned mortgage pricing engine (already built using 16 mortgage eligibility rules).

This new module will identify underserved communities across the USA (starting with New York State), analyze their needs using external datasets, and then generate a tailored mortgage solution for fast delivery to that community.  
This module MUST be compatible with and callable by the larger engine.

===============================================
A. MODULE NAME
===============================================
"CommunityInsightEngine" — an add-on to the existing mortgage pricing engine.

It has three main responsibilities:
1. Identify underserved communities.
2. Generate community-level mortgage intelligence.
3. Produce a community-tailored mortgage product recommendation using the 16-rule engine's logic.

===============================================
B. MODULE GOALS
===============================================
The module must:

1. Profile underserved communities in the USA.
2. Start with New York State — counties, zip codes, boroughs of NYC.
3. Allow user to select:
   - State
   - County
   - City / Borough
   - ZIP Code
   - Census Tract (optional)
4. Pull or simulate community-level data:
   - Median income
   - Area Median Income (AMI)
   - Homeownership rate
   - Rent burden
   - Demographics (race/ethnicity distribution)
   - Average credit score range
   - Average DTI patterns
   - First-time buyer % estimate
   - Foreclosure/bankruptcy density
   - Housing stock (1–4 unit vs condo vs manufactured)
   - Property value trends
   - Mortgage denial rates (HMDA-like patterns)
   - FHA/VA/USDA penetration
   - Conforming vs high-balance mix
   - ZIP Code high-cost designation (FHFA)
5. Identify underserved signals:
   - Low homeownership (<45%)
   - High rent burden (>30%)
   - High mortgage denial rates (>25%)
   - AMI < 80%
   - Predominantly minority census tracts (>50% Black/Hispanic/Tribal)
   - Persistent poverty
   - Low credit score clusters (avg < 680)
   - High % of first-time buyers
   - High foreclosure rates

6. Produce **Community Mortgage Persona**:
   - Buyer profile summary
   - Credit profile
   - Income distribution
   - Typical loan sizes
   - High-density borrowers needing:
     - Down-payment assistance
     - Lower LLPAs
     - First-time homebuyer credits
     - Nontraditional credit support
     - High-balance or low-balance loans depending on area
     - Condos vs SFR solutions

7. Recommend best-fitting mortgage strategies:
   - Conforming Standard 97% LTV (if FTHB requirement met)
   - HomeReady (AMI-based)
   - FHA (credit-challenged communities)
   - VA (veteran-heavy communities)
   - USDA (rural communities)
   - High-balance products (NYC, Westchester, Long Island)
   - Down Payment Assistance (DPA) integrations (state or ZIP)
   - LLPA waivers (FTHB + AMI)
   - MI optimization (standard vs reduced coverage)
   - Second-unit or multi-unit pathway where common

8. Generate **Community Tailored Loan Product**:
   - Using the pricing engine’s 16-rule system.
   - Return eligibility + pricing (LLPA + base price).
   - Include recommended:
     - Target rate range
     - Recommended MI structure
     - Reserve strategy
     - Coaching/education required
     - DU-vs-manual guidance
     - Avoidance flags (HPML, HOEPA, high HCLTV)

9. Provide **Community Quick Serve Blueprint**:
   - How a lender should set up:
     - Loan officers dedicated to this community
     - Partnerships (local non-profits, credit unions, housing authorities)
     - Multilingual communication needs
     - Average required borrower education
     - Pre-approved checklists for underserved borrowers
     - Optimized workflow for fast approvals
   - Provide a structured output (JSON + Human-readable)

===============================================
C. TECHNICAL REQUIREMENTS
===============================================
The module MUST:

1. Be fully compatible with the mortgage pricing engine you built earlier.
2. Accept:
   - `ScenarioInput`
   - `GeographyInput` (state / county / ZIP / census tract)
3. Return:
   - `CommunityProfile`
   - `CommunityMortgagePersona`
   - `CommunityMortgageRecommendation`
   - `CommunityPricingRecommendation` (calls existing LLPA engine)
   - `CommunityQuickServePlan`
4. Follow the same coding structure:
   - Python 3.11+
   - High modularity
   - Dataclasses for all models
   - Rule-based architecture
   - Config-driven (CSV/Dict-based data files)
5. Include:
   - `models_community.py`
   - `community_engine.py`
   - `community_profiles.py`
   - `community_rules.py`
   - `community_recommendations.py`
   - `community_data_loader.py`
   - `tests_community/`

===============================================
D. COMMUNITY DATA ENGINE — REQUIREMENTS
===============================================
The module must simulate OR load real datasets (but allow replacement):

1. FHFA:
   - County High-Balance Limits
2. HUD:
   - AMI data
   - FMR rent data
3. Census:
   - Demographic distributions
   - Owner/renter ratios
4. CFPB HMDA:
   - Mortgage denial patterns
5. Credit Bureau Simulation:
   - Compute average FICO cluster
6. Internal Scoring:
   - Community Underserved Index (0–100)

Compute:

**UnderservedIndex =**  
   (1 − homeownership_rate) * 0.25  
 + (rent_burden_score)        * 0.20  
 + (denial_rate_score)        * 0.20  
 + (AMI_gap_score)            * 0.15  
 + (credit_gap_score)         * 0.10  
 + (minority_share_score)     * 0.10  

Return the index and classification:
- 80–100: Severely Underserved  
- 60–79: Underserved  
- 40–59: At-risk  
- < 40: Stable or Upward Mobility

===============================================
E. OUTPUT REQUIREMENTS
===============================================
The module’s output must include:

1. **Community Snapshot (NY Example – Harlem, Bronx, Queens, Yonkers)**  
2. **Top Underserved Signals**  
3. **Borrower Persona**  
4. **Recommended Mortgage Programs**  
5. **Detailed LLPA and Pricing Summary**  
6. **Risks & Compliance Notes (Fannie Mae aligned)**  
7. **Quick Serve Plan**  
   - Outreach strategy  
   - Education modules  
   - Prequalification workflow  
   - Credit repair or counseling  
   - MI options  
   - DPA integrations  
   - Auto-education for first-time buyers  

8. **Machine-readable output (JSON)** + **human-readable summary**

===============================================
F. IMPLEMENTATION FLOW
===============================================
You MUST implement the module in this order:

1. Design dataclasses.
2. Create the community data engine.
3. Build rules for identifying underserved areas.
4. Build a persona generator.
5. Build a mortgage recommendation engine that calls the existing 16-rule pricing engine.
6. Build quick-serve blueprint generator.
7. Provide examples for:
   - Harlem (10026 / 10027)
   - South Bronx (10453 / 10457 / 10460)
   - Jamaica, Queens (11432 / 11433)
   - Buffalo East Side (14211 / 14215)
8. Provide unit tests validating underserved detection, persona creation, and program match.

===============================================
G. OUTPUT FORMAT
===============================================
When responding, return ONLY:

- The full source code files.
- Embedded documentation.
- A README describing how to use the new CommunityInsightEngine.
- Example executions for New York communities.

Do NOT include external commentary outside code/docstrings.
