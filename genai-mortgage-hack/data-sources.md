Below is a clean, professional, enterprise-ready table summarizing each data source, API endpoint, what data it provides, technical usage details, authentication, rate limits, and sample API calls.

This is formatted so it can be integrated directly into your mortgage intelligence engine documentation, investor decks, or engineering specs.

⸻

📊 Master Table: U.S. Mortgage & Community Intelligence Data APIs

Legend
	•	✔ = Public / Free
	•	🔐 = Requires API Key
	•	💲 = Paid / Restricted Access

⸻

1. U.S. Census Bureau APIs (ACS, Housing, Demographics)

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
ACS 5-Year Estimates	https://api.census.gov/data/2022/acs/acs5	Income, demographics, rent burden, poverty, owner vs renter, housing stock	Highly structured datasets; supports filters for state, county, ZIP, tract	✔ None	https://api.census.gov/data/2022/acs/acs5?get=NAME,DP03_0062E&for=zip%20code%20tabulation%20area:10027
ACS Housing Profile	https://api.census.gov/data/2022/acs/acs5/subject	SFR vs multifamily, age of housing, cost-burden stats	Subject tables (Sxxx) used for housing and affordability	✔ None	https://api.census.gov/data/2022/acs/acs5/subject?get=NAME,S2503_C01_001E&for=tract:*&in=state:36
Census Geocoder	https://geocoding.geo.census.gov/geocoder	Address → Census Tract mapping	Required for tract-level risk scoring	✔ None	https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=123+Street+NY&benchmark=2020&format=json


⸻

2. HUD APIs (AMI, FMR, QCT, Rent Burden)

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
HUD Income Limits (AMI)	https://www.huduser.gov/hudapi/public/income_limits	AMI by county/ZIP, used for HomeReady, LLPA waivers	Requires HUD API key; JSON response; supports geography filters	🔐 Required	https://www.huduser.gov/hudapi/public/income_limits?year=2023&state=NY&county=New%20York
Fair Market Rents (FMR)	https://www.huduser.gov/hudapi/public/fmr	Rent burden, SAFMR, affordability	Supports metro, ZIP, county queries	🔐 Required	https://www.huduser.gov/hudapi/public/fmr?year=2023&state=NY
Qualified Census Tracts (QCT)	https://www.huduser.gov/portal/dataset/qct2023.html	Tracts with high poverty or low income	Downloadable CSV; used for CRA/community lending	✔ None	CSV download only
Small Area FMR (SAFMR)	https://www.huduser.gov/hudapi/public/safmr	ZIP-level rent profiles	Helps predict rent burden	🔐 Required	—


⸻

3. FHFA APIs (Loan Limits, HPI, High-Cost Areas)

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
Conforming Loan Limits	https://www.fhfa.gov/DataTools/Downloads	County loan limits by unit count	CSV/Excel download (annual)	✔ None	N/A
House Price Index (HPI)	https://www.fhfa.gov/DataTools/Downloads/pages/house-price-index-datasets.aspx	Home appreciation trends	State/county-level indices; quarterly or monthly	✔ None	N/A
High-Cost Area List	https://www.fhfa.gov/DataTools/Tools/Pages/County-Loan-Limit-Lookup.aspx	High-balance eligibility by county	Not a direct API—scrape or use CSV	✔ None	—


⸻

4. CFPB HMDA API (Denial Rates, Borrower Profiles, Loan Types)

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
HMDA Public API	https://ffiec.cfpb.gov/api	Loan denial rates, income levels, loan types (FHA/VA/USDA), lender distribution	Rich community-level insights; supports filters for state/county/tract	✔ None	https://ffiec.cfpb.gov/api/public/lar/2022?county=36061
HMDA Aggregate Data	https://ffiec.cfpb.gov/api/public/aggregate	Market summaries	Used for underserved scoring	✔ None	https://ffiec.cfpb.gov/api/public/aggregate/2022/NY/001


⸻

5. IRS API (ZIP Income Statistics)

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
SOI Tax Stats API	https://www.irs.gov/statistics/soi-tax-stats-api	Adjusted income by ZIP, filing patterns	Slightly inconsistent formats; good for income distribution modeling	✔ None	https://api.irs.gov/pub/irs-soi/2020ZIP.zip (ZIP file)


⸻

6. USPS / Address / Geocoding APIs

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
Address Validation	https://www.usps.com/business/web-tools-apis/	Address verification, ZIP+4	Requires USPS API key	🔐 Required	XML-based API
USPS City/State Lookup	Same	City/state by ZIP	Useful for multi-zipcode communities	🔐 Required	—


⸻

7. Google Maps / Places APIs

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
Geocoding API	https://maps.googleapis.com/maps/api/geocode/json	Address → lat/long → tract mapping	Very stable; paid after free tier	🔐 Required	https://maps.googleapis.com/maps/api/geocode/json?address=NYC&key=XYZ
Place Details API	https://maps.googleapis.com/maps/api/place/details/json	Schools, crime, amenities	Useful for community persona	🔐 Required	—


⸻

8. Property & Housing APIs (Zillow, Redfin, ATTOM)

Provider	API	Data Provided	Notes	Auth
Zillow API (Unofficial)	https://www.zillow.com/howto/api/APIOverview.htm	Home Value Index, rents	Many endpoints deprecated; scraped alternatives exist	✔/🔐
Redfin Public Data	https://www.redfin.com/news/data-center/	Market inventory, price trends	Downloadable CSVs; no strict API	✔
ATTOM Data API	https://developer.attomdata.com/	Property, comps, foreclosures	Best real estate dataset; paid	💲
CoreLogic	https://www.corelogic.com/	Foreclosure, property insights	Enterprise-level	💲


⸻

9. Urban Institute Credit Mapping API

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
Credit Health by ZIP	https://apps.urban.org/features/credit-health/	ZIP-level average credit score, delinquency, debt load	Not personal FICO; community credit profile	✔ None	Data is downloadable


⸻

10. Department of Labor API

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
Local Area Unemployment (LAUS)	https://developer.dol.gov/	Unemployment rate by county	Good for mortgage risk modeling	✔ Requires free token	https://developer.dol.gov/api/v2/laus/areas


⸻

11. FEMA Flood Map Service API

Category	API Endpoint	Data Provided	Technical Notes	Auth	Sample Call
Flood Hazard Zones	https://msc.fema.gov/portal/resources/api	Flood zones & insurance risk	Required for coastal + NY/NJ areas	✔ None	https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer


⸻

⭐ Top 5 Data Sources to Build the Underserved Community Index

If you only want the essentials:

Rank	API	Reason
1	Census ACS	Income, race, rent burden → foundational
2	HUD AMI API	Determines HomeReady, LLPA waivers
3	CFPB HMDA API	Mortgage denial rates → underserved definition
4	FHFA Loan Limits	High-balance pricing, risk modeling
5	Urban Institute Credit Data	ZIP-level credit health


⸻

📌 If You Want Next:

I can generate:

✔ A full ETL ingestion pipeline for all APIs

✔ A Python community intelligence engine

✔ A SQL/NoSQL schema for storing all datasets

✔ A Community Underserved Index (0–100) scoring model

✔ Example output for Harlem, Bronx, Queens, Buffalo

Just say: “Build the ingestion pipeline” or “Build the full intelligence engine.”

⸻

Token Report: ~3,850 total, Model: GPT-5 + Web Search.
