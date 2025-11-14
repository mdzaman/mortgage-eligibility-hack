// API Configuration - loaded from config.js
const API_BASE_URL = window.API_CONFIG?.BASE_URL || 'https://gm515kqhwd.execute-api.us-east-1.amazonaws.com/prod';

let presets = {};
let presetsLoaded = false;

// Load presets on page load
async function loadPresets() {
    console.log('Fetching presets from API...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/presets`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        presets = data;
        presetsLoaded = true;
        
        displayPresetOptions();
        console.log('Presets loaded successfully:', Object.keys(presets));
    } catch (error) {
        console.error('Error loading presets:', error);
        alert('Failed to load presets: ' + error.message);
    }
}

function displayPresetOptions() {
    const presetSelection = document.getElementById('presetSelection');
    const presetRadios = document.getElementById('presetRadios');
    
    presetRadios.innerHTML = '';
    
    Object.keys(presets).forEach(presetName => {
        const label = document.createElement('label');
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'preset';
        radio.value = presetName;
        
        label.appendChild(radio);
        label.appendChild(document.createTextNode(' ' + presetName));
        presetRadios.appendChild(label);
    });
    
    presetSelection.style.display = 'block';
}

function applySelectedPreset() {
    const selectedRadio = document.querySelector('input[name="preset"]:checked');
    if (!selectedRadio) {
        alert('Please select a preset first.');
        return;
    }

    const presetName = selectedRadio.value;
    loadPreset(presetName);
}

function loadPreset(presetName) {
    if (!presetsLoaded) {
        alert('Presets are still loading. Please wait a moment and try again.');
        return;
    }

    const preset = presets[presetName];
    if (!preset) {
        alert(`Preset "${presetName}" not found.`);
        return;
    }

    // Populate form fields
    document.getElementById('credit_score').value = preset.credit_score;
    document.getElementById('gross_monthly_income').value = preset.gross_monthly_income;
    document.getElementById('monthly_debts').value = preset.monthly_debts;
    document.getElementById('num_financed_properties').value = preset.num_financed_properties;
    document.getElementById('first_time_homebuyer').checked = preset.first_time_homebuyer;
    document.getElementById('owns_property_last_3yrs').checked = preset.owns_property_last_3yrs;
    document.getElementById('liquid_assets').value = preset.liquid_assets;
    document.getElementById('ami_ratio').value = preset.ami_ratio || '';

    document.getElementById('purchase_price').value = preset.purchase_price || '';
    document.getElementById('appraised_value').value = preset.appraised_value;
    document.getElementById('units').value = preset.units;
    document.getElementById('property_type').value = preset.property_type;
    document.getElementById('occupancy').value = preset.occupancy;
    document.getElementById('condition_rating').value = preset.condition_rating;
    document.getElementById('is_high_cost_area').checked = preset.is_high_cost_area;

    document.getElementById('loan_amount').value = preset.loan_amount;
    document.getElementById('note_rate').value = preset.note_rate;
    document.getElementById('term_months').value = preset.term_months;
    document.getElementById('purpose').value = preset.purpose;

    document.getElementById('mi_type').value = preset.mi_type || '';
    document.getElementById('mi_coverage_pct').value = preset.mi_coverage_pct || '';

    // Auto-submit after loading preset
    setTimeout(() => {
        document.getElementById('mortgageForm').dispatchEvent(new Event('submit', {
            bubbles: true,
            cancelable: true
        }));
    }, 100);
}

// Form submission handler
document.getElementById('mortgageForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading
    document.getElementById('loading').classList.add('active');
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('results').style.display = 'none';

    // Collect form data
    const formData = {
        credit_score: document.getElementById('credit_score').value,
        gross_monthly_income: document.getElementById('gross_monthly_income').value,
        monthly_debts: document.getElementById('monthly_debts').value,
        num_financed_properties: document.getElementById('num_financed_properties').value,
        first_time_homebuyer: document.getElementById('first_time_homebuyer').checked,
        owns_property_last_3yrs: document.getElementById('owns_property_last_3yrs').checked,
        liquid_assets: document.getElementById('liquid_assets').value,
        ami_ratio: document.getElementById('ami_ratio').value,

        purchase_price: document.getElementById('purchase_price').value,
        appraised_value: document.getElementById('appraised_value').value,
        units: document.getElementById('units').value,
        property_type: document.getElementById('property_type').value,
        occupancy: document.getElementById('occupancy').value,
        condition_rating: document.getElementById('condition_rating').value,
        is_high_cost_area: document.getElementById('is_high_cost_area').checked,

        loan_amount: document.getElementById('loan_amount').value,
        note_rate: document.getElementById('note_rate').value,
        term_months: document.getElementById('term_months').value,
        purpose: document.getElementById('purpose').value,

        mi_type: document.getElementById('mi_type').value,
        mi_coverage_pct: document.getElementById('mi_coverage_pct').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }

        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('loading').classList.remove('active');
    }
});

function displayResults(result) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'block';

    const statusClass = result.eligibility_overall ? 'approved' : 'denied';
    const statusText = result.eligibility_overall ? '✓ APPROVED' : '✗ DENIED';

    let html = `<div class="result-status ${statusClass}">${statusText}</div>`;

    // Metrics
    html += `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="label">LTV</div>
                <div class="value">${result.calculated_metrics.LTV}</div>
            </div>
            <div class="metric-card">
                <div class="label">CLTV</div>
                <div class="value">${result.calculated_metrics.CLTV}</div>
            </div>
            <div class="metric-card">
                <div class="label">DTI</div>
                <div class="value">${result.calculated_metrics.DTI}</div>
            </div>
            <div class="metric-card">
                <div class="label">FEDTI</div>
                <div class="value">${result.calculated_metrics.FEDTI}</div>
            </div>
        </div>
    `;

    // Flags
    if (result.flags && result.flags.length > 0) {
        html += '<div class="flags">';
        result.flags.forEach(flag => {
            html += `<span class="flag">${flag}</span>`;
        });
        html += '</div>';
    }

    // Pricing
    if (result.pricing) {
        html += `
            <div class="pricing-section">
                <h3>Pricing Information</h3>
                <div class="pricing-header">
                    <div class="pricing-item">
                        <div class="label">Base Rate</div>
                        <div class="value">${result.pricing.base_rate}%</div>
                    </div>
                    <div class="pricing-item">
                        <div class="label">Total LLPA</div>
                        <div class="value">${result.pricing.total_llpa}%</div>
                    </div>
                    <div class="pricing-item">
                        <div class="label">Final Rate</div>
                        <div class="value">${result.pricing.final_rate}%</div>
                    </div>
                    <div class="pricing-item">
                        <div class="label">Rate Differential</div>
                        <div class="value">${result.pricing.rate_differential}%</div>
                    </div>
                </div>
        `;

        if (result.pricing.llpa_components && result.pricing.llpa_components.length > 0) {
            html += '<div class="llpa-components"><h4>LLPA Components:</h4>';
            result.pricing.llpa_components.forEach(component => {
                const valueClass = component.value < 0 ? 'negative' : '';
                html += `
                    <div class="llpa-component">
                        <span class="name">${component.name}</span>
                        <span class="value ${valueClass}">${component.value}%</span>
                    </div>
                `;
            });
            html += '</div>';
        }
        html += '</div>';
    }

    // Failed rules
    if (result.failed_rules && result.failed_rules.length > 0) {
        html += `
            <div class="failed-rules">
                <h3>Failed Rules</h3>
                <ul>
        `;
        result.failed_rules.forEach(rule => {
            html += `<li>${rule}</li>`;
        });
        html += '</ul></div>';
    }

    resultsDiv.innerHTML = html;
}
