"""
Simple HTTP Server for Mortgage Engine UI (No external dependencies)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from mortgage_engine import (
    price_scenario,
    ScenarioInput,
    BorrowerProfile,
    PropertyProfile,
    LoanTerms,
    FinancingStructure
)


class MortgageHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open('templates/index.html', 'r') as f:
                self.wfile.write(f.read().encode())

        elif self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open('test_browser.html', 'r') as f:
                self.wfile.write(f.read().encode())

        elif self.path == '/test-presets':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open('test_presets.html', 'r') as f:
                self.wfile.write(f.read().encode())

        elif self.path == '/simple-test':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open('simple_test.html', 'r') as f:
                self.wfile.write(f.read().encode())

        elif self.path == '/diagnostic':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open('diagnostic.html', 'r') as f:
                self.wfile.write(f.read().encode())

        elif self.path == '/api/presets':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            # Load presets from presets.json file
            try:
                with open('presets.json', 'r') as f:
                    presets = json.load(f)
                self.wfile.write(json.dumps(presets).encode())
            except FileNotFoundError:
                error = {"error": "presets.json file not found"}
                self.wfile.write(json.dumps(error).encode())
            except json.JSONDecodeError:
                error = {"error": "Invalid JSON in presets.json"}
                self.wfile.write(json.dumps(error).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/evaluate':
            try:
                import sys
                print(f"[{self.path}] Received POST request", file=sys.stderr)
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                print(f"[{self.path}] Parsed request data", file=sys.stderr)

                # Build scenario from request
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

                # Handle MI if provided
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

                # Run the engine
                print(f"[{self.path}] Running price_scenario...", file=sys.stderr)
                result = price_scenario(scenario)
                print(f"[{self.path}] Scenario evaluated successfully", file=sys.stderr)

                # Format response
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

                print(f"[{self.path}] Sending response...", file=sys.stderr)

                # Convert response to JSON
                response_json = json.dumps(response)
                response_bytes = response_json.encode('utf-8')

                print(f"[{self.path}] Response JSON length: {len(response_json)} chars, {len(response_bytes)} bytes", file=sys.stderr)
                print(f"[{self.path}] Response first 100 chars: {response_json[:100]}", file=sys.stderr)

                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(response_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                self.wfile.write(response_bytes)
                self.wfile.flush()

                print(f"[{self.path}] Response sent successfully", file=sys.stderr)

            except Exception as e:
                print(f"[{self.path}] ERROR: {str(e)}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Enable logging for debugging
        import sys
        print(f"[HTTP] {format % args}", file=sys.stderr)


def run_server(port=3000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, MortgageHandler)
    print(f"🚀 Mortgage Engine Server running on http://localhost:{port}")
    print(f"📊 Access the UI at http://localhost:{port}")
    print(f"Press Ctrl+C to stop the server")
    httpd.serve_forever()


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    run_server(port)
