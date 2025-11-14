"""
Community Data Loader

Provides community-level data for mortgage intelligence analysis.
Currently contains simulated data for New York State communities.
Can be extended to load real data from Census, HUD, HMDA, FHFA APIs.

Data Sources Simulated:
- US Census (demographics, housing)
- HUD (AMI, FMR)
- FHFA (loan limits)
- CFPB HMDA (mortgage patterns)
- Credit bureau aggregates
"""

from typing import Dict, Optional, List
from models_community import (
    GeographyInput, DemographicProfile, EconomicProfile,
    HousingProfile, CreditProfile, MortgageMarketProfile
)


# ==================== New York State Data ====================

# Conforming and High-Balance Loan Limits (2024)
LOAN_LIMITS_NY = {
    # NYC Metro - High Cost
    "New York County": {  # Manhattan
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Kings County": {  # Brooklyn
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Queens County": {
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Bronx County": {
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Richmond County": {  # Staten Island
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Westchester County": {
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Nassau County": {
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Suffolk County": {
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Rockland County": {
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    "Putnam County": {
        "conforming": 766_550,
        "high_balance": 1_149_825,
        "is_high_cost": True
    },
    # Rest of NY - Standard Conforming
    "Erie County": {  # Buffalo
        "conforming": 766_550,
        "high_balance": None,
        "is_high_cost": False
    },
    "Monroe County": {  # Rochester
        "conforming": 766_550,
        "high_balance": None,
        "is_high_cost": False
    },
    "Onondaga County": {  # Syracuse
        "conforming": 766_550,
        "high_balance": None,
        "is_high_cost": False
    },
    "Albany County": {
        "conforming": 766_550,
        "high_balance": None,
        "is_high_cost": False
    }
}


# Community Profiles Database
COMMUNITY_DATA = {
    # ==================== NYC - Manhattan ====================
    "10026": {  # Harlem
        "name": "Harlem (10026)",
        "county": "New York County",
        "city": "New York",
        "borough": "Manhattan",
        "demographics": {
            "total_population": 52_000,
            "median_age": 34.5,
            "pct_white": 9.2,
            "pct_black": 47.8,
            "pct_hispanic": 35.1,
            "pct_asian": 3.2,
            "pct_native_american": 0.3,
            "pct_other": 4.4,
            "pct_minority": 90.8
        },
        "economics": {
            "median_household_income": 52_000,
            "area_median_income": 110_000,  # NYC HUD AMI
            "per_capita_income": 28_500,
            "poverty_rate": 26.5,
            "unemployment_rate": 9.8,
            "pct_below_50k": 48.0,
            "pct_50k_to_100k": 32.0,
            "pct_100k_to_200k": 15.0,
            "pct_above_200k": 5.0
        },
        "housing": {
            "total_housing_units": 28_000,
            "homeownership_rate": 18.2,
            "rental_rate": 78.5,
            "vacancy_rate": 3.3,
            "median_home_value": 625_000,
            "median_rent": 1_650,
            "rent_burden_rate": 58.3,
            "severe_rent_burden_rate": 32.1,
            "pct_single_family": 5.0,
            "pct_2_4_units": 12.0,
            "pct_5plus_units": 78.0,
            "pct_condo": 15.0,
            "pct_manufactured": 0.0
        },
        "credit": {
            "avg_credit_score": 652,
            "median_credit_score": 645,
            "pct_below_580": 22.0,
            "pct_580_to_619": 18.5,
            "pct_620_to_679": 28.0,
            "pct_680_to_739": 21.0,
            "pct_740_plus": 10.5,
            "avg_dti_ratio": 41.2,
            "pct_high_dti": 38.0,
            "foreclosure_rate": 4.2,
            "bankruptcy_rate": 3.8,
            "collection_rate": 35.0
        },
        "mortgage_market": {
            "total_applications": 850,
            "approval_rate": 42.0,
            "denial_rate": 38.5,
            "withdrawal_rate": 19.5,
            "top_denial_reasons": ["Credit history", "DTI", "Income verification"],
            "pct_conventional": 35.0,
            "pct_fha": 52.0,
            "pct_va": 3.0,
            "pct_usda": 0.0,
            "pct_purchase": 68.0,
            "pct_refinance": 28.0,
            "pct_cash_out": 4.0,
            "estimated_fthb_rate": 72.0,
            "avg_loan_amount": 485_000,
            "avg_ltv": 92.5,
            "avg_dti": 41.8,
            "avg_rate": 7.125
        }
    },

    # ==================== NYC - Bronx ====================
    "10453": {  # South Bronx
        "name": "South Bronx (10453)",
        "county": "Bronx County",
        "city": "New York",
        "borough": "Bronx",
        "demographics": {
            "total_population": 78_000,
            "median_age": 31.2,
            "pct_white": 3.8,
            "pct_black": 35.2,
            "pct_hispanic": 58.9,
            "pct_asian": 1.2,
            "pct_native_american": 0.2,
            "pct_other": 0.7,
            "pct_minority": 96.2
        },
        "economics": {
            "median_household_income": 32_500,
            "area_median_income": 110_000,
            "per_capita_income": 16_800,
            "poverty_rate": 38.2,
            "unemployment_rate": 14.5,
            "pct_below_50k": 72.0,
            "pct_50k_to_100k": 22.0,
            "pct_100k_to_200k": 5.0,
            "pct_above_200k": 1.0
        },
        "housing": {
            "total_housing_units": 32_000,
            "homeownership_rate": 9.5,
            "rental_rate": 87.2,
            "vacancy_rate": 3.3,
            "median_home_value": 385_000,
            "median_rent": 1_250,
            "rent_burden_rate": 65.8,
            "severe_rent_burden_rate": 42.3,
            "pct_single_family": 3.0,
            "pct_2_4_units": 15.0,
            "pct_5plus_units": 80.0,
            "pct_condo": 5.0,
            "pct_manufactured": 0.0
        },
        "credit": {
            "avg_credit_score": 618,
            "median_credit_score": 608,
            "pct_below_580": 32.5,
            "pct_580_to_619": 24.0,
            "pct_620_to_679": 23.0,
            "pct_680_to_739": 15.0,
            "pct_740_plus": 5.5,
            "avg_dti_ratio": 44.5,
            "pct_high_dti": 48.0,
            "foreclosure_rate": 6.8,
            "bankruptcy_rate": 5.2,
            "collection_rate": 48.0
        },
        "mortgage_market": {
            "total_applications": 420,
            "approval_rate": 28.5,
            "denial_rate": 52.0,
            "withdrawal_rate": 19.5,
            "top_denial_reasons": ["Credit history", "DTI", "Insufficient funds"],
            "pct_conventional": 18.0,
            "pct_fha": 68.0,
            "pct_va": 2.0,
            "pct_usda": 0.0,
            "pct_purchase": 78.0,
            "pct_refinance": 18.0,
            "pct_cash_out": 4.0,
            "estimated_fthb_rate": 85.0,
            "avg_loan_amount": 315_000,
            "avg_ltv": 95.2,
            "avg_dti": 45.2,
            "avg_rate": 7.50
        }
    },

    # ==================== NYC - Queens ====================
    "11432": {  # Jamaica, Queens
        "name": "Jamaica, Queens (11432)",
        "county": "Queens County",
        "city": "New York",
        "borough": "Queens",
        "demographics": {
            "total_population": 62_000,
            "median_age": 36.8,
            "pct_white": 8.5,
            "pct_black": 42.3,
            "pct_hispanic": 32.8,
            "pct_asian": 14.2,
            "pct_native_american": 0.3,
            "pct_other": 1.9,
            "pct_minority": 91.5
        },
        "economics": {
            "median_household_income": 58_000,
            "area_median_income": 110_000,
            "per_capita_income": 25_600,
            "poverty_rate": 18.5,
            "unemployment_rate": 7.8,
            "pct_below_50k": 38.0,
            "pct_50k_to_100k": 42.0,
            "pct_100k_to_200k": 16.0,
            "pct_above_200k": 4.0
        },
        "housing": {
            "total_housing_units": 24_500,
            "homeownership_rate": 42.5,
            "rental_rate": 54.8,
            "vacancy_rate": 2.7,
            "median_home_value": 525_000,
            "median_rent": 1_550,
            "rent_burden_rate": 52.0,
            "severe_rent_burden_rate": 28.5,
            "pct_single_family": 35.0,
            "pct_2_4_units": 28.0,
            "pct_5plus_units": 32.0,
            "pct_condo": 12.0,
            "pct_manufactured": 0.0
        },
        "credit": {
            "avg_credit_score": 668,
            "median_credit_score": 662,
            "pct_below_580": 18.0,
            "pct_580_to_619": 16.0,
            "pct_620_to_679": 30.0,
            "pct_680_to_739": 24.0,
            "pct_740_plus": 12.0,
            "avg_dti_ratio": 39.5,
            "pct_high_dti": 35.0,
            "foreclosure_rate": 3.8,
            "bankruptcy_rate": 2.9,
            "collection_rate": 28.0
        },
        "mortgage_market": {
            "total_applications": 1_250,
            "approval_rate": 58.0,
            "denial_rate": 28.0,
            "withdrawal_rate": 14.0,
            "top_denial_reasons": ["DTI", "Credit history", "LTV"],
            "pct_conventional": 48.0,
            "pct_fha": 42.0,
            "pct_va": 5.0,
            "pct_usda": 0.0,
            "pct_purchase": 72.0,
            "pct_refinance": 24.0,
            "pct_cash_out": 4.0,
            "estimated_fthb_rate": 58.0,
            "avg_loan_amount": 425_000,
            "avg_ltv": 88.5,
            "avg_dti": 40.2,
            "avg_rate": 6.875
        }
    },

    # ==================== Buffalo - East Side ====================
    "14211": {  # Buffalo East Side
        "name": "Buffalo East Side (14211)",
        "county": "Erie County",
        "city": "Buffalo",
        "borough": None,
        "demographics": {
            "total_population": 28_500,
            "median_age": 33.2,
            "pct_white": 12.5,
            "pct_black": 72.8,
            "pct_hispanic": 10.2,
            "pct_asian": 1.8,
            "pct_native_american": 1.2,
            "pct_other": 1.5,
            "pct_minority": 87.5
        },
        "economics": {
            "median_household_income": 28_500,
            "area_median_income": 68_000,
            "per_capita_income": 15_200,
            "poverty_rate": 42.5,
            "unemployment_rate": 16.2,
            "pct_below_50k": 78.0,
            "pct_50k_to_100k": 18.0,
            "pct_100k_to_200k": 3.5,
            "pct_above_200k": 0.5
        },
        "housing": {
            "total_housing_units": 13_200,
            "homeownership_rate": 32.5,
            "rental_rate": 62.8,
            "vacancy_rate": 4.7,
            "median_home_value": 85_000,
            "median_rent": 725,
            "rent_burden_rate": 58.0,
            "severe_rent_burden_rate": 35.0,
            "pct_single_family": 62.0,
            "pct_2_4_units": 32.0,
            "pct_5plus_units": 5.0,
            "pct_condo": 2.0,
            "pct_manufactured": 1.0
        },
        "credit": {
            "avg_credit_score": 598,
            "median_credit_score": 585,
            "pct_below_580": 38.0,
            "pct_580_to_619": 26.0,
            "pct_620_to_679": 22.0,
            "pct_680_to_739": 11.0,
            "pct_740_plus": 3.0,
            "avg_dti_ratio": 46.5,
            "pct_high_dti": 52.0,
            "foreclosure_rate": 12.5,
            "bankruptcy_rate": 8.2,
            "collection_rate": 55.0
        },
        "mortgage_market": {
            "total_applications": 185,
            "approval_rate": 32.0,
            "denial_rate": 48.0,
            "withdrawal_rate": 20.0,
            "top_denial_reasons": ["Credit history", "Property condition", "DTI"],
            "pct_conventional": 12.0,
            "pct_fha": 72.0,
            "pct_va": 8.0,
            "pct_usda": 2.0,
            "pct_purchase": 65.0,
            "pct_refinance": 25.0,
            "pct_cash_out": 10.0,
            "estimated_fthb_rate": 68.0,
            "avg_loan_amount": 72_000,
            "avg_ltv": 96.5,
            "avg_dti": 47.8,
            "avg_rate": 7.25
        }
    },

    # ==================== Rochester ====================
    "14605": {  # Rochester - Inner Loop East
        "name": "Rochester Inner Loop East (14605)",
        "county": "Monroe County",
        "city": "Rochester",
        "borough": None,
        "demographics": {
            "total_population": 18_200,
            "median_age": 32.5,
            "pct_white": 22.0,
            "pct_black": 58.5,
            "pct_hispanic": 14.8,
            "pct_asian": 2.5,
            "pct_native_american": 0.8,
            "pct_other": 1.4,
            "pct_minority": 78.0
        },
        "economics": {
            "median_household_income": 32_800,
            "area_median_income": 72_500,
            "per_capita_income": 17_500,
            "poverty_rate": 38.0,
            "unemployment_rate": 12.8,
            "pct_below_50k": 68.0,
            "pct_50k_to_100k": 26.0,
            "pct_100k_to_200k": 5.0,
            "pct_above_200k": 1.0
        },
        "housing": {
            "total_housing_units": 8_500,
            "homeownership_rate": 28.5,
            "rental_rate": 68.2,
            "vacancy_rate": 3.3,
            "median_home_value": 95_000,
            "median_rent": 825,
            "rent_burden_rate": 54.0,
            "severe_rent_burden_rate": 32.0,
            "pct_single_family": 48.0,
            "pct_2_4_units": 42.0,
            "pct_5plus_units": 8.0,
            "pct_condo": 3.0,
            "pct_manufactured": 0.5
        },
        "credit": {
            "avg_credit_score": 628,
            "median_credit_score": 615,
            "pct_below_580": 28.0,
            "pct_580_to_619": 22.0,
            "pct_620_to_679": 26.0,
            "pct_680_to_739": 18.0,
            "pct_740_plus": 6.0,
            "avg_dti_ratio": 43.5,
            "pct_high_dti": 45.0,
            "foreclosure_rate": 8.5,
            "bankruptcy_rate": 5.8,
            "collection_rate": 42.0
        },
        "mortgage_market": {
            "total_applications": 225,
            "approval_rate": 38.0,
            "denial_rate": 42.0,
            "withdrawal_rate": 20.0,
            "top_denial_reasons": ["Credit history", "DTI", "Property value"],
            "pct_conventional": 22.0,
            "pct_fha": 65.0,
            "pct_va": 8.0,
            "pct_usda": 1.0,
            "pct_purchase": 68.0,
            "pct_refinance": 28.0,
            "pct_cash_out": 4.0,
            "estimated_fthb_rate": 72.0,
            "avg_loan_amount": 82_000,
            "avg_ltv": 95.0,
            "avg_dti": 44.8,
            "avg_rate": 7.125
        }
    }
}


# ==================== Data Access Functions ====================

def get_community_data(zip_code: str) -> Optional[Dict]:
    """Get raw community data for a ZIP code."""
    return COMMUNITY_DATA.get(zip_code)


def get_loan_limits(county: str) -> Dict:
    """Get conforming and high-balance loan limits for a county."""
    return LOAN_LIMITS_NY.get(county, {
        "conforming": 766_550,
        "high_balance": None,
        "is_high_cost": False
    })


def load_demographics(data: Dict) -> DemographicProfile:
    """Load demographic profile from raw data."""
    demo = data["demographics"]
    return DemographicProfile(
        total_population=demo["total_population"],
        median_age=demo["median_age"],
        pct_white=demo["pct_white"],
        pct_black=demo["pct_black"],
        pct_hispanic=demo["pct_hispanic"],
        pct_asian=demo["pct_asian"],
        pct_native_american=demo["pct_native_american"],
        pct_other=demo["pct_other"],
        pct_minority=demo["pct_minority"],
        is_majority_minority=demo["pct_minority"] > 50.0
    )


def load_economics(data: Dict) -> EconomicProfile:
    """Load economic profile from raw data."""
    econ = data["economics"]
    ami_ratio = econ["median_household_income"] / econ["area_median_income"]
    return EconomicProfile(
        median_household_income=econ["median_household_income"],
        area_median_income=econ["area_median_income"],
        ami_ratio=ami_ratio,
        per_capita_income=econ["per_capita_income"],
        poverty_rate=econ["poverty_rate"],
        unemployment_rate=econ["unemployment_rate"],
        pct_below_50k=econ["pct_below_50k"],
        pct_50k_to_100k=econ["pct_50k_to_100k"],
        pct_100k_to_200k=econ["pct_100k_to_200k"],
        pct_above_200k=econ["pct_above_200k"]
    )


def load_housing(data: Dict, county: str) -> HousingProfile:
    """Load housing profile from raw data."""
    housing = data["housing"]
    limits = get_loan_limits(county)

    return HousingProfile(
        total_housing_units=housing["total_housing_units"],
        homeownership_rate=housing["homeownership_rate"],
        rental_rate=housing["rental_rate"],
        vacancy_rate=housing["vacancy_rate"],
        median_home_value=housing["median_home_value"],
        median_rent=housing["median_rent"],
        rent_burden_rate=housing["rent_burden_rate"],
        severe_rent_burden_rate=housing["severe_rent_burden_rate"],
        pct_single_family=housing["pct_single_family"],
        pct_2_4_units=housing["pct_2_4_units"],
        pct_5plus_units=housing["pct_5plus_units"],
        pct_condo=housing["pct_condo"],
        pct_manufactured=housing["pct_manufactured"],
        is_high_cost_area=limits["is_high_cost"],
        conforming_loan_limit=limits["conforming"],
        high_balance_loan_limit=limits.get("high_balance")
    )


def load_credit(data: Dict) -> CreditProfile:
    """Load credit profile from raw data."""
    credit = data["credit"]
    return CreditProfile(
        avg_credit_score=credit["avg_credit_score"],
        median_credit_score=credit["median_credit_score"],
        pct_below_580=credit["pct_below_580"],
        pct_580_to_619=credit["pct_580_to_619"],
        pct_620_to_679=credit["pct_620_to_679"],
        pct_680_to_739=credit["pct_680_to_739"],
        pct_740_plus=credit["pct_740_plus"],
        avg_dti_ratio=credit["avg_dti_ratio"],
        pct_high_dti=credit["pct_high_dti"],
        foreclosure_rate=credit["foreclosure_rate"],
        bankruptcy_rate=credit["bankruptcy_rate"],
        collection_rate=credit["collection_rate"]
    )


def load_mortgage_market(data: Dict) -> MortgageMarketProfile:
    """Load mortgage market profile from raw data."""
    market = data["mortgage_market"]
    return MortgageMarketProfile(
        total_applications=market["total_applications"],
        approval_rate=market["approval_rate"],
        denial_rate=market["denial_rate"],
        withdrawal_rate=market["withdrawal_rate"],
        top_denial_reasons=market["top_denial_reasons"],
        pct_conventional=market["pct_conventional"],
        pct_fha=market["pct_fha"],
        pct_va=market["pct_va"],
        pct_usda=market["pct_usda"],
        pct_purchase=market["pct_purchase"],
        pct_refinance=market["pct_refinance"],
        pct_cash_out=market["pct_cash_out"],
        estimated_fthb_rate=market["estimated_fthb_rate"],
        avg_loan_amount=market["avg_loan_amount"],
        avg_ltv=market["avg_ltv"],
        avg_dti=market["avg_dti"],
        avg_rate=market["avg_rate"]
    )


def get_available_communities() -> List[Dict]:
    """Get list of all available communities."""
    communities = []
    for zip_code, data in COMMUNITY_DATA.items():
        communities.append({
            "zip_code": zip_code,
            "name": data["name"],
            "city": data["city"],
            "county": data["county"],
            "borough": data.get("borough")
        })
    return communities
