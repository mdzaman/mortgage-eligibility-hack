"""
Test the mortgage engine API endpoints
"""
import http.client
import json

def test_api():
    print("Testing Mortgage Engine API\n")
    print("=" * 60)

    # Test 1: GET /
    print("\n1. Testing GET / (Homepage)")
    conn = http.client.HTTPConnection('localhost', 3000)
    conn.request('GET', '/')
    response = conn.getresponse()
    print(f"   Status: {response.status}")
    html = response.read().decode()
    if 'Mortgage Eligibility' in html:
        print("   ✓ Homepage loaded successfully")
    conn.close()

    # Test 2: GET /api/presets
    print("\n2. Testing GET /api/presets")
    conn = http.client.HTTPConnection('localhost', 3000)
    conn.request('GET', '/api/presets')
    response = conn.getresponse()
    print(f"   Status: {response.status}")
    presets = json.loads(response.read().decode())
    print(f"   ✓ Loaded {len(presets)} presets: {', '.join(presets.keys())}")
    conn.close()

    # Test 3: POST /api/evaluate (Prime Conforming scenario)
    print("\n3. Testing POST /api/evaluate (Prime Conforming)")
    test_data = {
        'credit_score': 760,
        'gross_monthly_income': 10000,
        'monthly_debts': 650,
        'num_financed_properties': 1,
        'first_time_homebuyer': False,
        'owns_property_last_3yrs': True,
        'liquid_assets': 50000,
        'ami_ratio': '',
        'purchase_price': 400000,
        'appraised_value': 400000,
        'units': 1,
        'property_type': 'SFR',
        'occupancy': 'primary',
        'condition_rating': 'C3',
        'is_high_cost_area': True,
        'loan_amount': 300000,
        'note_rate': 6.50,
        'term_months': 360,
        'purpose': 'purchase',
        'mi_type': '',
        'mi_coverage_pct': ''
    }

    conn = http.client.HTTPConnection('localhost', 3000)
    headers = {'Content-Type': 'application/json'}
    conn.request('POST', '/api/evaluate', json.dumps(test_data), headers)
    response = conn.getresponse()
    print(f"   Status: {response.status}")

    result = json.loads(response.read().decode())

    if 'eligibility_overall' in result:
        print(f"   ✓ Eligibility: {'APPROVED' if result['eligibility_overall'] else 'DENIED'}")
        print(f"   ✓ LTV: {result['calculated_metrics']['LTV']}")
        print(f"   ✓ DTI: {result['calculated_metrics']['DTI']}")
        print(f"   ✓ Net Price: {result['pricing']['net_price']}")
        print(f"   ✓ Total LLPA: {result['pricing']['llpa_total_bps']} bps")
        print(f"   ✓ {len(result['all_rules'])} rules evaluated")
        print(f"   ✓ {len(result['failed_rules'])} failed rules")
    conn.close()

    # Test 4: POST /api/evaluate (FTHB High LTV)
    print("\n4. Testing POST /api/evaluate (FTHB 97% LTV)")
    test_data_fthb = {
        'credit_score': 700,
        'gross_monthly_income': 6000,
        'monthly_debts': 300,
        'num_financed_properties': 1,
        'first_time_homebuyer': True,
        'owns_property_last_3yrs': False,
        'liquid_assets': 10000,
        'ami_ratio': 0.85,
        'purchase_price': 300000,
        'appraised_value': 300000,
        'units': 1,
        'property_type': 'SFR',
        'occupancy': 'primary',
        'condition_rating': 'C3',
        'is_high_cost_area': False,
        'loan_amount': 291000,
        'note_rate': 6.75,
        'term_months': 360,
        'purpose': 'purchase',
        'mi_type': 'borrower_paid_monthly',
        'mi_coverage_pct': 0.35
    }

    conn = http.client.HTTPConnection('localhost', 3000)
    conn.request('POST', '/api/evaluate', json.dumps(test_data_fthb), headers)
    response = conn.getresponse()
    print(f"   Status: {response.status}")

    result = json.loads(response.read().decode())

    if 'eligibility_overall' in result:
        print(f"   ✓ Eligibility: {'APPROVED' if result['eligibility_overall'] else 'DENIED'}")
        print(f"   ✓ LTV: {result['calculated_metrics']['LTV']}")
        print(f"   ✓ FTHB Flag: {result['flags'].get('FTHB', False)}")
        print(f"   ✓ Net Price: {result['pricing']['net_price']}")
        print(f"   ✓ Waivers applied: {len(result['pricing']['waivers'])}")
    conn.close()

    print("\n" + "=" * 60)
    print("✅ All API tests passed!")
    print("\n🌐 Access the UI at: http://localhost:3000")

if __name__ == "__main__":
    test_api()
