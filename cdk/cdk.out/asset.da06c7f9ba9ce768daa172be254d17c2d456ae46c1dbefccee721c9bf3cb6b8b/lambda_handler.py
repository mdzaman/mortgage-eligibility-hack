import json
from mortgage_engine import (
    price_scenario,
    ScenarioInput,
    BorrowerProfile,
    PropertyProfile,
    LoanTerms,
    FinancingStructure
)

def handler(event, context):
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    # Normalize path
    if path.startswith('/prod'):
        path = path[5:]
    if path.startswith('/api'):
        path = path[4:]
    
    if path == '/' and method == 'GET':
        try:
            with open('templates/index.html', 'r') as f:
                html_content = f.read()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': html_content
            }
        except:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Mortgage Eligibility Engine</h1><p>API is running. Use /evaluate and /presets endpoints.</p>'
            }
    
    elif path == '/evaluate' and method == 'POST':
        try:
            data = json.loads(event.get('body', '{}'))
            
            borrower = BorrowerProfile(
                credit_score=int(data['credit_score']),
                gross_monthly_income=float(data['gross_monthly_income']),
                monthly_debts={"other_debts": float(data.get('monthly_debts', 0))},
                num_financed_properties=int(data['num_financed_properties']),
                first_time_homebuyer=data.get('first_time_homebuyer', False),
                owns_property_last_3yrs=data.get('owns_property_last_3yrs', True),
                liquid_assets_after_closing=float(data['liquid_assets']),
                doc_type="full",
                ami_ratio=float(data['ami_ratio']) if data.get('ami_ratio') else None
            )

            property_info = PropertyProfile(
                purchase_price=float(data.get('purchase_price')) if data.get('purchase_price') else None,
                appraised_value=float(data['appraised_value']),
                units=int(data['units']),
                property_type=data['property_type'],
                occupancy=data['occupancy'],
                condition_rating=data.get('condition_rating', 'C3'),
                state=data.get('state', 'CA'),
                county=data.get('county', 'Unknown'),
                is_high_cost_area=data.get('is_high_cost_area', False)
            )

            loan = LoanTerms(
                loan_amount=float(data['loan_amount']),
                note_rate=float(data['note_rate']),
                term_months=int(data.get('term_months', 360)),
                arm=data.get('arm', False),
                purpose=data['purpose'],
                product_type=data.get('product_type', 'fixed'),
                channel=data.get('channel', 'conforming')
            )

            mi_type = data.get('mi_type')
            mi_coverage = float(data['mi_coverage_pct']) if data.get('mi_coverage_pct') else None

            financing = FinancingStructure(
                subordinate_liens=[],
                mi_type=mi_type if mi_type else None,
                mi_coverage_pct=mi_coverage
            )

            scenario = ScenarioInput(
                borrower=borrower,
                property=property_info,
                loan=loan,
                financing=financing
            )

            result = price_scenario(scenario)

            response = {
                'eligibility_overall': result.eligibility_overall,
                'calculated_metrics': {
                    'LTV': f"{result.calculated_metrics.get('LTV', 0):.2%}",
                    'CLTV': f"{result.calculated_metrics.get('CLTV', 0):.2%}",
                    'HCLTV': f"{result.calculated_metrics.get('HCLTV', 0):.2%}",
                    'DTI': f"{result.calculated_metrics.get('DTI', 0):.2%}",
                    'channel': result.calculated_metrics.get('channel', 'N/A'),
                    'reserves_required': f"${result.calculated_metrics.get('reserves_required_dollars', 0):,.0f}",
                    'reserves_months': f"{result.calculated_metrics.get('reserves_required_months', 0):.0f}"
                },
                'flags': result.flags,
                'pricing': {
                    'base_rate': f"{result.pricing.base_rate:.3f}%",
                    'base_price': f"{result.pricing.base_price:.3f}%",
                    'llpa_total_bps': f"{result.pricing.llpa_total_bps:.2f}",
                    'net_price': f"{result.pricing.net_price:.3f}%",
                    'components': [
                        {
                            'name': c.name,
                            'value_bps': f"{c.value_bps:+.2f}",
                            'reason': c.reason
                        }
                        for c in result.pricing.components
                    ],
                    'waivers': result.pricing.waivers_applied,
                    'notes': result.pricing.notes
                },
                'failed_rules': [
                    {
                        'rule_name': r.rule_name,
                        'messages': r.messages
                    }
                    for r in result.rule_results if not r.eligible
                ],
                'all_rules': [
                    {
                        'rule_name': r.rule_name,
                        'eligible': r.eligible,
                        'messages': r.messages
                    }
                    for r in result.rule_results
                ]
            }

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(response)
            }

        except Exception as e:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }
    
    elif path == '/presets' and method == 'GET':
        presets = {
            'prime_conforming': {
                'name': 'Prime Conforming Purchase',
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
        }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(presets)
        }
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found'})
    }
