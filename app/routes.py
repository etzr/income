from flask import Blueprint, render_template, request, jsonify
from app.calculators import get_calculator, get_available_countries, get_available_years
from datetime import datetime
import numpy as np
from flask import request
import os

main = Blueprint('main', __name__)

def log_submission(data):
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'submissions.log')
    
    ip_address = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] IP: {ip_address}\n"
    for key, value in data.items():
        log_entry += f"{key}: {value}\n"
    log_entry += "\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)


def safe_float(value, default=0.0):
    if value == '':
        return default
    try:
        return float(value)
    except ValueError:
        return default

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/get_options')
def get_options():
    countries = get_available_countries()
    tax_years = get_available_years()
    return jsonify({
        'countries': countries,
        'taxYears': tax_years
    })

@main.route('/api/get_states/<country>')
def get_states(country):
    calculator = get_calculator(country)
    if calculator:
        states = calculator.get_states()
        return jsonify({'states': states})
    return jsonify({'error': 'Country not supported'}), 400

@main.route('/api/get_cities/<country>/<state>')
def get_cities(country, state):
    calculator = get_calculator(country)
    if calculator:
        cities = calculator.get_cities(state)
        return jsonify({'cities': cities})
    return jsonify({'error': 'Country not supported'}), 400

@main.route('/api/salary_distribution/<country>')
def get_salary_distribution(country):
    # These are example values. Replace with actual data for each country.
    distributions = {
        'China': {'median': 260412, 'std_dev': 88889},
        'Singapore': {'median': 69396, 'std_dev': 43000},
        'United States': {'median': 58100, 'std_dev': 27336}
    }
    
    if country not in distributions:
        return jsonify({'error': 'Country not found'}), 404

    median = distributions[country]['median']
    std_dev = distributions[country]['std_dev']
    
    mu = np.log(median**2 / np.sqrt(median**2 + std_dev**2))
    sigma = np.sqrt(np.log(1 + (std_dev**2 / median**2)))

    # Generate log-normal distribution values
    s = np.random.lognormal(mean=mu, sigma=sigma, size=10000)

    # Calculate specific percentiles
    percentiles = [10, 25, 50, 75, 90]
    percentile_values = np.percentile(s, percentiles)

    # Density curve x and y values
    x = np.linspace(min(s), max(s), 100)
    y = (1 / (x * sigma * np.sqrt(2 * np.pi))) * np.exp(-((np.log(x) - mu)**2 / (2 * sigma**2)))

    return jsonify({
        'x': x.tolist(),
        'y': y.tolist(),
        'median': np.exp(mu + sigma**2 / 2),  # Median of the log-normal distribution
        'percentiles': dict(zip(percentiles, percentile_values))
    })


@main.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    country = data.get('country')
    income = safe_float(data.get('income', 0))
    state = data.get('state', '')
    city = data.get('city', '')
    year = int(data.get('tax-year', datetime.now().year))
    is_resident = data.get('is_resident', True)

    log_submission(data)

    calculator = get_calculator(country)
    if calculator:
        try:
            if country == 'Singapore':
                age = int(data.get('age', 35))
                result = calculator.calculate(income, state, city, age, year, is_resident)
            elif country == 'United States':
                contribution_percent = safe_float(data.get('401k-contribution'))
                employer_match_percent = safe_float(data.get('employer-match'))
                employer_match_limit = safe_float(data.get('employer-match-limit'))
                result = calculator.calculate(income, state, city, year, is_resident, 
                                              contribution_percent, employer_match_percent, employer_match_limit)
            elif country == 'China':
                result = calculator.calculate(income, state, city, year, is_resident)
            else:
                return jsonify({'error': 'Unsupported country'}), 400

            result['country'] = country
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Country not supported'}), 400