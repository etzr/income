from flask import Blueprint, render_template, request, jsonify
from app.calculators import get_calculator, get_available_countries, get_available_years
from datetime import datetime

main = Blueprint('main', __name__)

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

@main.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    country = data.get('country')
    income = safe_float(data.get('income', 0))
    state = data.get('state', '')
    city = data.get('city', '')
    year = int(data.get('tax-year', datetime.now().year))
    is_resident = data.get('is_resident', True)

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
            else:
                return jsonify({'error': 'Unsupported country'}), 400

            result['country'] = country
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'Country not supported'}), 400