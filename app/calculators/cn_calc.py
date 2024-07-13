import csv
import os
from datetime import datetime

def load_tax_rates(file_name):
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', file_name)
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            if year not in rates:
                rates[year] = []
            rates[year].append({
                'income_threshold_from': float(row['taxable_income_min']),
                'income_threshold_to': float(row['taxable_income_max']),
                'rate': float(row['tax_rate']),
                'quick_deduction': float(row['quick_deduction'])
            })
    return rates

RESIDENT_TAX_RATES = load_tax_rates('cn_resident_tax_rates.csv')
NON_RESIDENT_TAX_RATES = load_tax_rates('cn_non_resident_tax_rates.csv')

def load_social_insurance_rates():
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cn_social_insurance_rates.csv')
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            if year not in rates:
                rates[year] = {}
            rates[year][row['category']] = {
                'pension': float(row['pension']),
                'medical': float(row['medical']),
                'unemployment': float(row['unemployment']),
                'work_injury': float(row['work_injury']),
                'maternity': float(row['maternity'])
            }
    return rates

SOCIAL_INSURANCE_RATES = load_social_insurance_rates()

def get_states():
    # China doesn't have states, so we'll return major cities or provinces
    return ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chongqing", "Tianjin", "Other"]

def get_cities(state):
    # For simplicity, we'll return the same city as the state/province
    return [state]

def get_available_years():
    return sorted(list(set(RESIDENT_TAX_RATES.keys()) | set(NON_RESIDENT_TAX_RATES.keys()) | set(SOCIAL_INSURANCE_RATES.keys())), reverse=True)

def calculate_income_tax(taxable_income, year, is_resident):
    if year not in RESIDENT_TAX_RATES or year not in NON_RESIDENT_TAX_RATES:
        raise ValueError(f"No tax data available for year {year}")

    if is_resident:
        tax_rates = RESIDENT_TAX_RATES[year]
        for bracket in tax_rates:
            if taxable_income <= bracket['income_threshold_to']:
                tax = taxable_income * bracket['rate'] - bracket['quick_deduction']
                return max(tax, 0)  # Ensure tax is not negative
        # If income exceeds the highest bracket
        tax = taxable_income * tax_rates[-1]['rate'] - tax_rates[-1]['quick_deduction']
        return max(tax, 0)
    else:
        tax_rates = NON_RESIDENT_TAX_RATES[year]
        monthly_income = taxable_income / 12
        for bracket in tax_rates:
            if monthly_income <= bracket['income_threshold_to']:
                monthly_tax = monthly_income * bracket['rate'] - bracket['quick_deduction']
                return monthly_tax * 12
        # If income exceeds the highest bracket
        monthly_tax = monthly_income * tax_rates[-1]['rate'] - tax_rates[-1]['quick_deduction']
        return monthly_tax * 12

def calculate_social_insurance(income, year):
    if year not in SOCIAL_INSURANCE_RATES:
        raise ValueError(f"No social insurance data available for year {year}")

    employee_rates = SOCIAL_INSURANCE_RATES[year]['employee']
    # employer_rates = SOCIAL_INSURANCE_RATES[year]['employer']
    
    employee_contribution = sum(income * rate for rate in employee_rates.values())
    # employer_contribution = sum(income * rate for rate in employer_rates.values())
    employer_contribution = income * 0.07
    
    return employee_contribution, employer_contribution

def calculate(income, state=None, city=None, year=None, is_resident=True):
    if year is None:
        year = datetime.now().year
    else:
        year = int(year)

    if year not in RESIDENT_TAX_RATES or year not in NON_RESIDENT_TAX_RATES or year not in SOCIAL_INSURANCE_RATES:
        raise ValueError(f"No data available for year {year}")

    if is_resident:
        standard_deduction = 60000
        employee_social_insurance, employer_social_insurance = calculate_social_insurance(income, year)
        taxable_income = max(income - employee_social_insurance - standard_deduction, 0)
    else:
        standard_deduction = 0
        employee_social_insurance = employer_social_insurance = 0
        taxable_income = income

    income_tax = calculate_income_tax(taxable_income, year, is_resident)

    # Calculate net income
    net_income = income - income_tax - employee_social_insurance

    # Prepare the detailed breakdown
    breakdown = {
        'year': year,
        'is_resident': is_resident,
        'gross_income': income,
        'standard_deduction': standard_deduction,
        'taxable_income': taxable_income,
        'income_tax': income_tax,
        'employee_social_insurance': employee_social_insurance,
        'employer_social_insurance': employer_social_insurance,
        'net_income': net_income,
        'total_compensation': income + employer_social_insurance,
        'real_compensation': income - income_tax + employer_social_insurance
    }

    return breakdown