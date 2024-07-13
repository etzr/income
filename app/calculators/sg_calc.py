import csv
import os
from datetime import datetime
import math

def load_tax_rates():
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sg_tax_rates.csv')
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            if year not in rates:
                rates[year] = []
            rates[year].append({
                'chargeable_income': float(row['chargeable_income']) if row['chargeable_income'] else math.inf,
                'rate': float(row['rate']),
                'income_threshold': float(row['income_threshold'])
            })
    return rates

def load_cpf_rates():
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sg_cpf_rates.csv')
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            if year not in rates:
                rates[year] = {}
            age_group = (int(row['min_age']), int(row['max_age']))
            rates[year][age_group] = {
                'employee_rate': float(row['employee_rate']),
                'employer_rate': float(row['employer_rate'])
            }
    return rates

TAX_RATES = load_tax_rates()
CPF_RATES = load_cpf_rates()

def get_states():
    # Singapore is a city-state, so we'll just return 'Singapore'
    return ['Singapore']

def get_cities(state=None):
    # Singapore is a city-state, so we'll just return 'Singapore'
    return ['Singapore']

def get_available_years():
    return sorted(list(TAX_RATES.keys()), reverse=True)

def calculate_income_tax(income, year, is_resident):
    tax_resident = 0
    tax_non_resident = income * 0.15  # Flat 15% for non-residents

    # Calculate tax using resident rates
    chargeable_income = income
    for bracket in TAX_RATES[year]:
        if chargeable_income > bracket['income_threshold']:
            taxable_amount = min(chargeable_income - bracket['income_threshold'], bracket['chargeable_income'])
            tax_resident += taxable_amount * bracket['rate']
        else:
            break

    if is_resident:
        return tax_resident
    else:
        # For non-residents, return the higher of 15% flat rate or tax calculated using resident rates
        return max(tax_resident, tax_non_resident)

def calculate_cpf(income, age, year):
    monthly_income = income / 12  # Convert annual income to monthly
    monthly_cpf_wage_ceiling = 6800  # Monthly ceiling of $6,000
    
    # Calculate CPF for each month
    monthly_employee_cpf = 0
    monthly_employer_cpf = 0
    
    for (min_age, max_age), rates in CPF_RATES[year].items():
        if min_age <= age <= max_age:
            cpf_income = min(monthly_income, monthly_cpf_wage_ceiling)
            monthly_employee_cpf = cpf_income * rates['employee_rate']
            monthly_employer_cpf = cpf_income * rates['employer_rate']
            break
    
    # Convert monthly CPF to annual
    annual_employee_cpf = monthly_employee_cpf * 12
    annual_employer_cpf = monthly_employer_cpf * 12
    
    return annual_employee_cpf, annual_employer_cpf

def calculate(income, state=None, city=None, age=35, year=None, is_resident=True):
    if year is None:
        year = datetime.now().year

    if year not in TAX_RATES or year not in CPF_RATES:
        raise ValueError(f"No data available for year {year}")

    income_tax = calculate_income_tax(income, year, is_resident)
    
    if is_resident:
        employee_cpf, employer_cpf = calculate_cpf(income, age, year)
    else:
        employee_cpf = 0
        employer_cpf = 0

    # Calculate net income
    net_income = income - income_tax - employee_cpf

    # Prepare the detailed breakdown
    breakdown = {
        'year': year,
        'is_resident': is_resident,
        'gross_income': income,
        'income_tax': income_tax,
        'employee_cpf_contribution': employee_cpf,
        'employer_cpf_contribution': employer_cpf,
        'net_income': net_income,
        'total_compensation': income + employer_cpf,
        'real_compensation': income - income_tax + employer_cpf
    }

    return breakdown