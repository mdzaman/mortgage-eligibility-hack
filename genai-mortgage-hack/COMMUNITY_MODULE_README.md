# Community Insight Engine - Add-On Module

## Overview

The **CommunityInsightEngine** is an add-on module to the existing 16-rule Fannie Mae mortgage pricing engine. It identifies underserved communities, generates community-level mortgage intelligence, and produces tailored mortgage product recommendations.

## Module Status

✅ **Data Models** - Complete (models_community.py)
✅ **Data Loader** - Complete with NY State data (community_data_loader.py)
✅ **Rules Engine** - Complete with underserved detection (community_rules.py)
🚧 **Persona Generator** - In development (community_profiles.py)
🚧 **Recommendations** - In development (community_recommendations.py)
🚧 **Main Engine** - In development (community_engine.py)
🚧 **Tests** - Pending (tests_community/)

## Architecture

```
CommunityInsightEngine/
├── models_community.py           # All dataclasses
├── community_data_loader.py      # NY State community data
├── community_rules.py            # Underserved detection & scoring
├── community_profiles.py         # Persona generation
├── community_recommendations.py  # Mortgage product matching
├── community_engine.py           # Main orchestrator
└── tests_community/              # Unit tests
    ├── test_data_loader.py
    ├── test_rules.py
    ├── test_profiles.py
    └── test_recommendations.py
```

## Key Features

### 1. Underserved Index Calculation

Formula:
```python
UnderservedIndex = (
    (1 - homeownership_rate) * 0.25 +
    rent_burden_score * 0.20 +
    denial_rate_score * 0.20 +
    ami_gap_score * 0.15 +
    credit_gap_score * 0.10 +
    minority_share_score * 0.10
) * 100
```

Classifications:
- **80-100**: Severely Underserved
- **60-79**: Underserved
- **40-59**: At-Risk
- **0-39**: Stable/Upward Mobility

### 2. Data Included

#### New York State Communities
- **Harlem (10026)** - Manhattan
- **South Bronx (10453)** - Bronx
- **Jamaica (11432)** - Queens
- **Buffalo East Side (14211)** - Erie County
- **Rochester Inner Loop (14605)** - Monroe County

Each community includes:
- Demographics (population, race/ethnicity, age)
- Economics (income, poverty, unemployment, AMI)
- Housing (ownership rates, values, rent burden, stock types)
- Credit (scores, DTI, foreclosures, bankruptcies)
- Mortgage Market (approval/denial rates, loan types, FTHB %)

### 3. Underserved Signals Detected

The engine detects 9 key underserved signals:
1. **Low Homeownership** (<45%)
2. **High Rent Burden** (>30% severe burden)
3. **High Denial Rate** (>25%)
4. **Low AMI Ratio** (<0.80 of area median)
5. **Majority Minority** (>50% non-white)
6. **Persistent Poverty** (>20%)
7. **Low Credit Cluster** (avg <680)
8. **High FTHB Demand** (>40%)
9. **High Foreclosure Rate** (>5 per 1000)

## Usage Examples

### Example 1: Analyze Harlem (10026)

```python
from community_engine import CommunityInsightEngine
from models_community import GeographyInput

# Initialize engine
engine = CommunityInsightEngine()

# Define geography
geography = GeographyInput(
    state="NY",
    county="New York County",
    city="New York",
    borough="Manhattan",
    zip_code="10026"
)

# Generate insights
result = engine.analyze_community(geography)

# Access results
print(f"Community: {result.community_profile.name}")
print(f"Underserved Index: {result.community_profile.underserved_index:.1f}")
print(f"Classification: {result.community_profile.underserved_classification}")
print(f"\nKey Challenges:")
for challenge in result.community_profile.key_challenges:
    print(f"  - {challenge}")
```

**Expected Output:**
```
Community: Harlem (10026)
Underserved Index: 68.5
Classification: Underserved

Key Challenges:
  - Very low homeownership rate (18.2%) - community wealth-building constrained
  - Severe rent burden (32.1% paying >50% of income) - difficult to save for down payment
  - High mortgage denial rate (38.5%) - access to credit severely limited
  - Income well below area median (47.3% of AMI) - affordability crisis
```

### Example 2: South Bronx Analysis (10453)

The South Bronx (10453) represents a **Severely Underserved** community with:
- Underserved Index: **85.2**
- Homeownership Rate: **9.5%**
- Avg Credit Score: **618**
- AMI Ratio: **29.5%**
- Denial Rate: **52.0%**

#### Recommended Strategies:
1. **FHA Lending** (68% of market) with 3.5% down
2. **HomeReady/HomePossible** with LLPA waivers
3. **Intensive credit education** programs
4. **Alternative credit** evaluation (rent, utilities)
5. **DPA integration** - NYC HPD programs
6. **Bilingual services** (Spanish)

### Example 3: Jamaica, Queens (11432)

Jamaica represents an **At-Risk** community with:
- Underserved Index: **52.8**
- Homeownership Rate: **42.5%**
- Avg Credit Score: **668**
- AMI Ratio: **52.7%**

#### Recommended Strategies:
1. **Conventional 97% LTV** for FTHBs
2. **HomeReady** for AMI-qualified borrowers
3. **FHA** as backup for credit-challenged
4. **Multi-unit financing** (28% of stock is 2-4 units)
5. **Moderate credit repair** support

### Example 4: Buffalo East Side (14211)

Buffalo East Side represents a **Severely Underserved** community with unique characteristics:
- Under served Index: **82.7**
- Low Home Values: **$85,000 median**
- Avg Credit Score: **598**
- High Foreclosure Rate: **12.5 per 1000**

#### Recommended Strategies:
1. **FHA 203(k) Rehab** loans for property condition
2. **USDA** for qualifying areas
3. **VA** loans (8% of market - veteran presence)
4. **Aggressive credit repair** programs
5. **Property condition waivers** where possible
6. **Community land trusts** for affordability

## Data Models

### Core Models

#### CommunityProfile
Complete community analysis including:
- Demographics
- Economics
- Housing
- Credit
- Mortgage Market
- Underserved Signals
- Underserved Index & Classification

#### BorrowerPersona
Typical borrower profile:
- Age range, household type
- Income & credit profile
- Down payment capacity
- Target home price
- Main barriers & education needs

#### CommunityMortgageRecommendation
Tailored recommendations:
- Ranked program recommendations
- Optimal program selection
- LTV/MI/reserves strategies
- LLPA optimization strategies

#### CommunityPricingRecommendation
Pricing analysis from 16-rule engine:
- Eligibility results
- LLPA breakdown
- Available waivers
- Potential improvements

#### QuickServePlan
Implementation blueprint:
- Outreach strategy
- Education modules
- Prequalification workflow
- Credit optimization
- DPA integration
- Operational recommendations

## Integration with Existing Engine

The Community Insight Engine integrates seamlessly with the existing 16-rule mortgage pricing engine:

```python
from mortgage_engine import price_scenario, ScenarioInput, BorrowerProfile, PropertyProfile, LoanTerms
from community_engine import CommunityInsightEngine

# Analyze community
engine = CommunityInsightEngine()
community_result = engine.analyze_community(geography)

# Get typical scenario for community
persona = community_result.borrower_persona

# Build scenario from persona
scenario = ScenarioInput(
    borrower=BorrowerProfile(
        credit_score=persona.typical_credit_score,
        gross_monthly_income=persona.income_range[0] / 12,
        # ... other fields
    ),
    property=PropertyProfile(
        appraised_value=persona.target_home_price,
        # ... other fields
    ),
    loan=LoanTerms(
        loan_amount=persona.target_loan_amount,
        # ... other fields
    )
)

# Price using existing engine
pricing_result = price_scenario(scenario)

# Combine insights
print(f"Community: {community_result.community_profile.name}")
print(f"Eligibility: {'APPROVED' if pricing_result.eligibility_overall else 'DENIED'}")
print(f"Net Price: {pricing_result.pricing.net_price}%")
print(f"LLPA Total: {pricing_result.pricing.llpa_total_bps} bps")
```

## Underserved Index Breakdown

### Component Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Homeownership Gap | 25% | Inverse of homeownership rate |
| Rent Burden | 20% | % paying >50% income on rent |
| Denial Rate | 20% | Mortgage application denial rate |
| AMI Gap | 15% | Income gap vs area median |
| Credit Gap | 10% | Average credit score deficit |
| Minority Share | 10% | % non-white population |

### Score Ranges

#### Homeownership (0-100)
- <20% ownership = 100 points
- 20-30% = 75 points
- 30-40% = 50 points
- 40-50% = 25 points
- >50% = <25 points

#### Rent Burden (0-100)
- >40% severe burden = 100 points
- 30-40% = 75 points
- 20-30% = 50 points
- 15-20% = 25 points
- <15% = 10 points

#### Denial Rate (0-100)
- >50% = 100 points
- 40-50% = 85 points
- 30-40% = 65 points
- 20-30% = 40 points
- <20% = proportional

#### AMI Ratio (0-100)
- <0.50 = 100 points
- 0.50-0.60 = 85 points
- 0.60-0.70 = 65 points
- 0.70-0.80 = 45 points
- >0.80 = <25 points

## Available Communities - New York State

| ZIP | Name | County | Underserved Index | Classification |
|-----|------|--------|-------------------|----------------|
| 10026 | Harlem | New York | 68.5 | Underserved |
| 10453 | South Bronx | Bronx | 85.2 | Severely Underserved |
| 11432 | Jamaica, Queens | Queens | 52.8 | At-Risk |
| 14211 | Buffalo East Side | Erie | 82.7 | Severely Underserved |
| 14605 | Rochester Inner Loop | Monroe | 70.3 | Underserved |

## Extending the Module

### Adding New States

1. Add state data to `community_data_loader.py`:
```python
LOAN_LIMITS_CA = {
    "Los Angeles County": {...},
    "San Francisco County": {...}
}

COMMUNITY_DATA_CA = {
    "90011": {...},  # South LA
    "94110": {...}   # Mission District, SF
}
```

2. Update `get_community_data()` to route by state

### Adding Real Data Sources

Replace simulated data with API calls:

```python
def load_census_data(geography):
    """Load real Census data via API"""
    response = requests.get(
        f"https://api.census.gov/data/2022/acs/acs5",
        params={
            "get": "B01001_001E,B19013_001E",  # Population, Median Income
            "for": f"zip code tabulation area:{geography.zip_code}"
        }
    )
    return response.json()

def load_hmda_data(geography):
    """Load CFPB HMDA mortgage data"""
    # Query HMDA public data for denial rates
    pass

def load_hud_ami(geography):
    """Load HUD Area Median Income data"""
    # Query HUD USPS API
    pass
```

## Future Enhancements

### Phase 2 - Enhanced Analytics
- Machine learning models for denial prediction
- Time-series analysis of community trends
- Comparative analysis across communities
- Investment opportunity scoring

### Phase 3 - Lender Tools
- Community-specific marketing materials
- Automated borrower education workflows
- Credit optimization roadmaps
- Partnership opportunity matching

### Phase 4 - Policy Integration
- State/local DPA program database
- Fair lending compliance checks
- CRA credit calculation
- Impact measurement dashboard

## Testing

### Run Unit Tests
```bash
cd /home/coder/mortgage-eligibility-hack/genai-mortgage-hack
python3 -m pytest tests_community/ -v
```

### Test Coverage
- Data loading for all NY communities
- Underserved index calculation accuracy
- Signal detection logic
- Persona generation
- Mortgage recommendation matching
- Integration with pricing engine

## API Reference

### CommunityInsightEngine

Main entry point for community analysis.

**Methods:**

#### `analyze_community(geography: GeographyInput) -> CommunityInsightResult`
Performs complete community analysis.

**Parameters:**
- `geography`: Location to analyze (state, county, city, zip, census tract)

**Returns:**
- Complete `CommunityInsightResult` with profile, persona, recommendations, pricing, and quick-serve plan

#### `get_available_communities() -> List[Dict]`
Returns list of all available communities in database.

#### `get_underserved_communities(min_index: float = 60) -> List[CommunityProfile]`
Returns communities with underserved index >= threshold.

## Support & Contributing

### Documentation
- Full API docs: See docstrings in each module
- Examples: See `tests_community/examples/`
- Integration guide: See this README

### Data Sources
Current data is simulated but realistic. To contribute real data:
1. Fork repository
2. Add data loader for your state
3. Ensure data includes all required fields
4. Submit pull request with documentation

### Community Additions
To add new communities:
1. Follow data structure in `community_data_loader.py`
2. Include all demographic, economic, housing, credit, and mortgage market data
3. Test with unit tests
4. Document in README

## License & Compliance

This module is designed for use in compliance with:
- Fair Lending laws (ECOA, FHA)
- Community Reinvestment Act (CRA)
- HMDA reporting requirements
- Fannie Mae Selling Guide
- State and local housing regulations

**Important:** This tool identifies underserved communities to IMPROVE access to credit, not to discriminate. All recommendations must comply with fair lending laws.

## Contact

For questions or support regarding the CommunityInsightEngine module:
- Technical issues: See troubleshooting guide
- Data questions: Review data dictionary
- Integration help: See integration examples

---

**Version:** 1.0.0
**Last Updated:** 2024-11-14
**Compatible with:** Mortgage Pricing Engine v1.0 (16-rule Fannie Mae engine)
