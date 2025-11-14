You are a senior mortgage technology architect and Python engineer. Your task is to DESIGN AND IMPLEMENT a self-contained mortgage eligibility and pricing engine for U.S. residential mortgages, grounded in Fannie Mae’s 16 core eligibility dimensions.

You must output:
1) Clean, production-ready Python code (modules + tests) implementing the engine.
2) Clear in-code documentation and docstrings.
3) A short README-style usage guide embedded as a multiline string.

The engine must be self-contained, with all rule logic configurable via JSON/YAML-like structures so it can be reused and extended.


------------------------------------------------
A. OVERALL GOAL & SCOPE
------------------------------------------------

Build a Python package called `mortgage_engine` that:

1. Accepts a single input scenario object for a U.S. residential loan:
   - Borrower profile
   - Property profile
   - Loan terms
   - Market/pricing context (for LLPA and base-rate lookups)

2. Evaluates **eligibility** against Fannie Mae-style rules across ALL 16 dimensions:

   1. Loan-to-Value and Combined LTV (LTV / CLTV / HCLTV)
   2. Credit Score (FICO)
   3. Debt-to-Income Ratio (DTI)
   4. Property Type (1–4 unit, condo, co-op, manufactured)
   5. Occupancy Type (primary, second home, investment)
   6. Loan Purpose (purchase, limited cash-out refi, cash-out refi)
   7. Loan Amount Limits (conforming vs. high-balance)
   8. Mortgage Insurance (MI) requirements (LTV > 80%)
   9. Reserve Requirements (months of PITIA, including additional for multiple properties)
   10. Number of Financed Properties (1–10 and related constraints)
   11. Income Documentation Type (full-doc requirement for conforming)
   12. Property Condition & Appraisal Acceptability (C1–C6; reject C5/C6 unless cured)
   13. AUS vs Manual Underwriting Thresholds (DU “Approve/Eligible” vs manual caps)
   14. First-Time Homebuyer (FTHB) status (97% LTV logic, education flags)
   15. High-Cost / HPML / HCLTV flags (HOEPA ineligible; HPML allowed but flagged)
   16. Loan-Level Price Adjustments (LLPAs) and waivers/credits

3. Produces a **composite result**:
   - `eligibility_overall` (boolean)
   - per-rule `eligibility` & `messages`
   - computed `LTV / CLTV / HCLTV / DTI`
   - required MI coverage (if any)
   - required reserves (dollars and months)
   - risk flags (HPML, HOEPA, manual-UW-only, etc.)
   - a **pricing result** containing:
     - base rate (from stubbed or configurable rate sheet)
     - total LLPA points (% of loan)
     - list of applied LLPA components (credit/LTV, occupancy, property type, high-balance, MI-min, etc.)
     - any LLPA waivers or credits (FTHB + AMI, HomeReady-style, counseling credit)
     - final net price and implied rate/points mapping (simplified)

4. Is implemented in a modular, testable architecture:
   - Core domain models
   - Rule engine layer (each rule as a class/function)
   - Pricing / LLPA engine
   - Orchestration function: `price_scenario()`


------------------------------------------------
B. TECHNOLOGY & STRUCTURE
------------------------------------------------

1. Language & Style
   - Python 3.11+
   - Use standard library only (no external dependencies), unless absolutely necessary.
   - Type hints for all public functions.
   - PEP8-compliant, clear docstrings.
   - Avoid global state; configuration is passed explicitly.

2. Package Layout (single file is acceptable but prefer modular structure):

   mortgage_engine/
     __init__.py
     models.py          # dataclasses for inputs/outputs
     config.py          # default rule thresholds / LLPA tables as Python dicts
     rules/
       __init__.py
       rule_ltv.py
       rule_credit.py
       rule_dti.py
       rule_property_type.py
       rule_occupancy.py
       rule_purpose.py
       rule_loan_amount.py
       rule_mi.py
       rule_reserves.py
       rule_financed_props.py
       rule_income_doc.py
       rule_property_condition.py
       rule_aus_manual.py
       rule_fthb.py
       rule_high_cost_hpml_hcltv.py
       rule_llpa.py
     engine.py          # orchestrates rules, aggregates results
     pricing.py         # LLPA and base pricing logic (rate/price grid, mapping)
     demo.py            # simple CLI/examples
     tests/
       test_rules_*.py
       test_integration.py

You may compress into fewer files if necessary, but keep logical separation clear in code (e.g. via classes).


------------------------------------------------
C. DATA MODELS
------------------------------------------------

Define core dataclasses in `models.py`:

1. BorrowerProfile
   - `credit_score: int`
   - `gross_monthly_income: float`
   - `monthly_debts: dict[str, float]`  # includes proposed PITIA keyed separately
   - `num_financed_properties: int`
   - `first_time_homebuyer: bool`
   - `owns_property_last_3yrs: bool`    # or derive from FTHB
   - `liquid_assets_after_closing: float`
   - `doc_type: str`                    # "full", "non_qm", etc. (only "full" allowed for conforming)
   - optional: `ami_ratio: float | None`  # borrower income / area median income

2. PropertyProfile
   - `purchase_price: float | None`
   - `appraised_value: float`
   - `units: int`                 # 1–4
   - `property_type: str`         # "SFR", "Condo", "Coop", "Manufactured", "PUD", "MixedUse"
   - `occupancy: str`             # "primary", "second_home", "investment"
   - `condition_rating: str`      # "C1"..."C6"
   - `state: str`
   - `county: str`
   - `is_high_cost_area: bool`
   - `project_type: str | None`   # "condo_project", "none", etc.

3. LoanTerms
   - `loan_amount: float`
   - `note_rate: float`           # nominal interest rate
   - `term_months: int`
   - `arm: bool`
   - `purpose: str`               # "purchase", "rate_term_refi", "cash_out_refi"
   - `product_type: str`          # "fixed", "arm"
   - `channel: str`               # "conforming", "high_balance"

4. FinancingStructure
   - `subordinate_liens: list[dict]` with keys:
     - `type: str`                # "second_mortgage", "heloc"
     - `current_balance: float`
     - `credit_limit: float | None`
   - `mi_type: str | None`        # "borrower_paid_monthly", "lender_paid", "single", None
   - `mi_coverage_pct: float | None`
   - `base_rate_sheet_id: str | None`  # for pricing stub selection

5. ScenarioInput
   - Bundle:
     - `borrower: BorrowerProfile`
     - `property: PropertyProfile`
     - `loan: LoanTerms`
     - `financing: FinancingStructure`

6. RuleResult
   - `rule_name: str`
   - `eligible: bool`
   - `messages: list[str]`
   - `metrics: dict[str, float | str | bool]`  # e.g. {"LTV": 0.95, "CLTV": 0.98}

7. PricingComponent
   - `name: str`                  # e.g. "LLPA_credit_LTV", "LLPA_investment_property"
   - `value_bps: float`           # points as percentage, e.g. 125 = 1.25%
   - `reason: str`

8. PricingResult
   - `base_rate: float`
   - `base_price: float`
   - `llpa_total_bps: float`
   - `components: list[PricingComponent]`
   - `waivers_applied: list[str]`
   - `net_price: float`
   - `notes: list[str]`

9. EngineResult
   - `eligibility_overall: bool`
   - `rule_results: list[RuleResult]`
   - `pricing: PricingResult | None`
   - `calculated_metrics: dict[str, float]` # LTV/CLTV/HCLTV/DTI/reserves, etc.
   - `flags: dict[str, bool]`              # {"HPML": True, "HOEPA": False, "ManualUWOnly": False}


------------------------------------------------
D. IMPLEMENTATION OF THE 16 RULES
------------------------------------------------

Implement each rule as a pure function or a small class implementing a `run()` method, taking `ScenarioInput` and a shared `config` dict, returning `RuleResult`.

Use a central `config.py` that holds **default thresholds** and **LLPA tables** in structured Python dicts (e.g., nested by credit/LTV, etc.), and make everything data-driven so rules can be tuned without changing code.

For each rule, implement:

1. Rule 1 – LTV / CLTV / HCLTV
   - Compute:
     - `value = min(purchase_price, appraised_value)` if purchase, else `appraised_value`.
     - `LTV = first_lien_amount / value`
     - `CLTV = (first_lien_amount + sum(subordinate_balances)) / value`
     - `HCLTV = (first_lien_amount + sum(heloc_credit_limits)) / value`
   - Truncate to 2 decimals and round up to nearest whole percent.
   - Check against LTV/CLTV/HCLTV limits from config matrix keyed by:
     - occupancy
     - property units
     - purpose
     - channel ("conforming"/"high_balance")
   - Return metrics: LTV, CLTV, HCLTV, max_allowed.

2. Rule 2 – Credit Score
   - Use `borrower.credit_score` as representative FICO.
   - Check minimal score requirements from config:
     - standard conforming: 620, ARMs: 640, high-balance or 2–4 units: possibly 680/700.
   - Allow future extension for multiple borrowers (compute lowest median).
   - Record whether scenario requires DU Approval to exceed manual thresholds.

3. Rule 3 – DTI
   - Compute total monthly debts including:
     - PITIA for subject property (can approximate with simple formula or pass in from input).
     - All recurring obligations in `monthly_debts`.
   - `DTI = total_debt / gross_monthly_income`.
   - Compare with:
     - `max_dti_du = 0.50`
     - `max_dti_manual_base = 0.36`
     - `max_dti_manual_with_comp = 0.45`
   - Tag result with whether this DTI requires DU (e.g. if >0.45 and ≤0.50).

4. Rule 4 – Property Type
   - Validate `property_type` ∈ allowed set.
   - Enforce:
     - 1–4 unit only.
     - Co-op rules: e.g. no investment co-ops (flag ineligible if occupancy="investment" and type="Coop").
     - Manufactured: require additional flags; cap LTV from config; may require DU-only.
   - Return any property-type-driven constraints (max LTV override, etc.).

5. Rule 5 – Occupancy
   - Validate occupancy ∈ {"primary", "second_home", "investment"}.
   - Enforce:
     - second_home must be 1-unit.
     - investment property rules for LTV and reserves (but actual LTV limits handled via rule 1 config).
   - Set flags for risk (e.g. `is_investor_loan=True`).

6. Rule 6 – Loan Purpose
   - Validate purpose ∈ {"purchase", "rate_term_refi", "cash_out_refi"}.
   - Determine:
     - Is this limited cash-out or true cash-out? Use simple `cash_to_borrower` calculation from config (or stub).
   - Enforce:
     - cash-out LTV caps distinct from purchase/LCOR.
     - 6-month title seasoning for cash-out (via config boolean if we want to approximate).
   - Attach purpose to metrics.

7. Rule 7 – Loan Amount Limits
   - From config, determine:
     - baseline 1–4 unit limits.
     - high-cost max limits if `is_high_cost_area=True`.
   - Decide:
     - category: "conforming" vs "high_balance" vs "jumbo" (jumbo => ineligible for Fannie path).
   - Check `loan_amount` <= max for unit/area.
   - Return classification and max allowed.

8. Rule 8 – MI Requirements
   - If `LTV > 0.80` and loan is conventional:
     - Require MI; compute standard coverage from config table by LTV and term.
   - If MI not provided in input and required: mark eligibility = False.
   - Compute `coverage_pct_required` and `coverage_gap` if chosen coverage < required.
   - Flag whether LLPA for “minimum MI” should be added (if coverage < standard).

9. Rule 9 – Reserves
   - Compute required reserves in months:
     - Based on occupancy, units, DTI, cash-out, and number of financed properties.
     - Use config rules:
       - 2–4 unit primary: 6 months subject PITIA.
       - second home: min 2 months.
       - investment: min 6 months.
       - plus additional % of UPB of other properties (2%/4%/6%).
   - Convert to required dollars and compare to `liquid_assets_after_closing`.
   - Return required vs available; mark eligibility accordingly.

10. Rule 10 – Number of Financed Properties
    - Use `num_financed_properties`.
    - Enforce:
      - max 10 financed properties for second-home/investment scenarios.
      - if >6, require:
        - DU-only (no manual).
        - min credit score (e.g. 720).
        - additional reserve percentage as per config.
    - Output classification: "standard (≤6)", "extended (7–10)", or "ineligible (>10)".

11. Rule 11 – Income Documentation
    - Enforce:
      - Only "full" or "standard" doc type allowed for conforming.
      - If `doc_type != "full"` mark as ineligible for Fannie conforming channel.
    - Provide explanation message; leave a hook for future non-QM extensions.

12. Rule 12 – Property Condition & Appraisal Acceptability
    - If `condition_rating in {"C5","C6"}` ⇒ ineligible, message: "Requires repair to C4 or better".
    - Optionally accept `structural_issues: bool` flag from property metrics.
    - Provide condition metrics: `condition_rating`, `acceptability`.

13. Rule 13 – AUS vs Manual Underwriting Thresholds
    - Using DTI and credit score, determine:
      - whether scenario must be DU-only (e.g. DTI > 0.45 OR >6 financed properties).
      - whether scenario is within manual caps (DTI ≤ 0.36 or ≤0.45 with comp factors).
    - Provide flags:
      - `requires_du: bool`
      - `manual_eligible: bool`
    - This rule does not simulate DU, but approximates constraints; leave placeholder for DU integration.

14. Rule 14 – First-Time Homebuyer
    - Determine `is_first_time` based on `first_time_homebuyer` and `owns_property_last_3yrs`.
    - If `LTV > 0.95` on standard conforming product:
      - Require `any_first_time=True` else mark ineligible.
    - Determine whether homeownership education is required:
      - If `all_borrowers_first_time` and LTV > 95%, set `education_required=True`.
    - Provide flags for LLPA waivers:
      - if FTHB and `ami_ratio <= 1.0` (or 1.2 in high-cost), mark eligible for LLPA waiver.

15. Rule 15 – High-Cost / HPML / HCLTV
    - Accept as inputs (or compute simple approximations):
      - `APR`, `APOR`, `points_and_fees_pct`.
    - Determine:
      - `is_hpml = APR >= APOR + hpml_margin` (e.g. 1.5%).
      - `is_hoepa = APR >= APOR + hoepa_margin OR points_and_fees_pct > threshold`.
    - If `is_hoepa`: mark overall eligibility False.
    - For HPML, mark flag HPML=True but not ineligible.
    - Also enforce HCLTV max from LTV matrix config.

16. Rule 16 – LLPAs & Waivers
    - Implement a configurable LLPA matrix:
      - Base grid: by credit score band & LTV bucket.
      - Add-on adjustments: occupancy, units, property type, high-balance, MI-min, etc.
    - Steps:
      1. Map scenario to:
         - credit_band (e.g. "720-739")
         - ltv_bucket (e.g. "80.01-85")
         - occupancy_type, property_type, is_high_balance, is_investment, is_second_home, is_manufactured, etc.
      2. Sum all applicable LLPA points.
      3. Apply waivers:
         - If first-time homebuyer AND `ami_ratio <= threshold`: waive all standard LLPAs.
         - If `homeownership_counseling=True` and config specifies credit (e.g. 0.125%), subtract that from LLPA.
      4. Return:
         - total LLPA points,
         - breakdown list of components.

    - This rule should not decide eligibility unless LLPA > some configured maximum (optional). It primarily feeds pricing.


------------------------------------------------
E. PRICING ENGINE LOGIC
------------------------------------------------

In `pricing.py`:

1. Base Rate Sheet Stub
   - Implement a simple base rate sheet as a Python dict:
     - Keys: `("conforming","fixed_30")`, with base prices for a grid of note rates (e.g. 5.50%, 5.75%, 6.00%) at par for **top tier** (e.g. 780+ FICO, ≤60% LTV, primary).
   - Provide a function:
     - `get_base_price(note_rate: float, product_key: tuple, config: dict) -> float`
   - For simplicity, you can:
     - Use linear interpolation between two nearest rates, or
     - Use a simple mapping (exact rate -> price) and state that other rates are not allowed in the demo.

2. Apply LLPA
   - Convert `llpa_total_bps` to price adjustment:
     - `price_adjustment = - llpa_total_bps / 100.0`  # since 100 bps = 1 point
   - Final net price = base_price + price_adjustment.
   - Build `PricingResult` with:
     - base_rate
     - base_price
     - llpa_total_bps
     - components
     - waivers_applied
     - net_price

3. HPML / APR notes (optional)
   - Approximate APR by adding simple assumptions:
     - e.g. assume total points equal LLPA and single origination fee.
   - If HPML, append a note: “Loan is HPML, ensure escrows and HPML requirements are met.”


------------------------------------------------
F. ENGINE ORCHESTRATION
------------------------------------------------

In `engine.py`:

1. Implement `run_rules(scenario: ScenarioInput, config: dict) -> list[RuleResult]`:
   - Execute each of the 16 rules in a logical order (some rules depend on earlier metrics, e.g. LTV before MI & LLPA).
   - Pass along intermediate metrics via a shared `context` dict that can accumulate:
     - computed LTV/CLTV/HCLTV
     - DTI
     - reserves required
     - flags (HPML, FTHB waiver-eligible, etc.)

2. Implement `aggregate_eligibility(rule_results: list[RuleResult]) -> bool`:
   - Overall eligibility is True if and only if ALL mandatory rules are `eligible=True`.
   - Some rules (LLPA) may never set `eligible=False` – they just provide pricing; treat them as non-fatal.
   - HOEPA rule: if HOEPA flagged, mark overall False.

3. Implement `price_scenario(scenario: ScenarioInput, config: dict) -> EngineResult`:
   - Step 1: run rules & build `rule_results`, `context`.
   - Step 2: compute overall eligibility.
   - Step 3: if not eligible, you may still compute LLPA/pricing for diagnostic purposes but mark clearly as ineligible.
   - Step 4: call pricing engine:
     - choose `base_rate` (use `scenario.loan.note_rate` as chosen rate).
     - `base_price = get_base_price(...)`
     - `llpa_result = rule_llpa.run(...)`
     - build `PricingResult`.
   - Step 5: assemble `EngineResult`:
     - `eligibility_overall`
     - all `rule_results`
     - `pricing`
     - `calculated_metrics` from context
     - `flags` (HPML, HOEPA, ManualUWOnly, etc.)

4. Provide a simple CLI/demo in `demo.py`:
   - Hard-code 2–3 scenarios:
     a) Prime conforming purchase (FICO 760, 75% LTV, primary, 30-year fixed).
     b) High-LTV FTHB (97% LTV, FICO 700, first-time, low AMI).
     c) Investment property cash-out (75% LTV, multiple financed properties).
   - Print:
     - overall eligibility
     - top rule failures, if any
     - pricing summary: base rate, net price, LLPA breakdown.


------------------------------------------------
G. TESTING
------------------------------------------------

Create unit tests in `tests/` for:

1. LTV/CLTV/HCLTV computations:
   - Cases with and without HELOC.
   - Boundary at 80% / 95% / 97%.

2. DTI:
   - Cases at 36%, 45%, 50% boundaries.

3. Loan amount limits:
   - Conforming vs high-balance vs jumbo.

4. MI rule:
   - LTV 79.99% (no MI) vs 80.01% (MI required).
   - Standard vs minimum MI coverage.

5. Reserve rule:
   - Primary 1-unit (0–2 months).
   - 2–4 unit and investment with required 6+ months and extra for multiple properties.

6. Financed property rule:
   - 4, 7, 11 financed property cases.

7. FTHB rule:
   - 97% LTV with and without first-time buyer.
   - AMI <= 100% triggers LLPA waiver flag.

8. HOEPA/HPML rule:
   - Scenario flagged as HOEPA (must be ineligible).
   - HPML but HOEPA false (mark warning only).

9. LLPA engine:
   - Known credit/LTV combos produce expected total LLPA per test config.
   - Waiver removes LLPA for FTHB <= AMI.

10. Integration:
   - A full scenario that passes all rules and yields a consistent PricingResult.
   - A full scenario that fails due to LTV or HOEPA but still returns pricing diagnostics.

Use `assert` statements and some tolerance for floating-point comparisons.


------------------------------------------------
H. CONFIGURABILITY & DOCUMENTATION
------------------------------------------------

1. Config
   - In `config.py`, define:
     - `LTV_LIMITS` by occupancy, units, purpose, channel.
     - `LOAN_LIMITS` by units and high-cost flag.
     - `MI_COVERAGE_TABLE`.
     - `RESERVE_RULES`.
     - `FINANCED_PROPERTY_RULES`.
     - `HPML_HOEPA_THRESHOLDS`.
     - `LLPA_MATRICES` including:
       - `BASE_CREDIT_LTV_GRID`
       - `ADJUST_OCCUPANCY`
       - `ADJUST_PROPERTY_TYPE`
       - `ADJUST_HIGH_BALANCE`
       - `ADJUST_MIN_MI`
       - `WAIVER_FTHB_AMI`
       - `CREDITS_COUNSELING`, `CREDITS_HOMEREADY`, etc.
   - Use realistic but simplified values; clearly comment that they are approximations and should be replaced with real matrices in production.

2. Documentation
   - Include a module-level docstring in `engine.py` explaining:
     - Purpose of the engine.
     - High-level data flow.
   - Include a `README_TEXT` multiline string explaining:
     - How to construct a `ScenarioInput`.
     - How to call `price_scenario()`.
     - How to interpret `EngineResult`.
     - How to plug different LLPA/limit matrices via `config`.

3. Clarity
   - For each rule, include comments:
     - Which Fannie Mae dimension it corresponds to (1–16).
     - What assumptions you made.
     - Which parts should be parameterized for real-world deployment.


------------------------------------------------
I. OUTPUT FORMAT
------------------------------------------------

When you respond, output ONLY:
- The Python code for all modules (can be in one file but structured with clear sections and comments as described).
- The embedded README-style usage guide.

Do NOT output explanations outside of comments/docstrings. The goal is to be able to copy-paste your output into a file or package and run the engine and tests directly.
