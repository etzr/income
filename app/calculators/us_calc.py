import csv
import os
from datetime import datetime
import math

US_CITIES = {
    "Alabama": ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa"],
    "Alaska": ["Anchorage", "Fairbanks", "Juneau", "Sitka", "Ketchikan"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale"],
    "Arkansas": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro"],
    "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Sacramento"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood"],
    "Connecticut": ["Bridgeport", "New Haven", "Stamford", "Hartford", "Waterbury"],
    "Delaware": ["Wilmington", "Dover", "Newark", "Middletown", "Smyrna"],
    "Florida": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah"],
    "Hawaii": ["Honolulu", "Hilo", "Kailua", "Kapolei", "Kaneohe"],
    "Idaho": ["Boise", "Meridian", "Nampa", "Idaho Falls", "Pocatello"],
    "Illinois": ["Chicago", "Aurora", "Naperville", "Rockford", "Joliet"],
    "Indiana": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel"],
    "Iowa": ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City", "Iowa City"],
    "Kansas": ["Wichita", "Overland Park", "Kansas City", "Olathe", "Topeka"],
    "Kentucky": ["Louisville", "Lexington", "Bowling Green", "Owensboro", "Covington"],
    "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles"],
    "Maine": ["Portland", "Lewiston", "Bangor", "South Portland", "Auburn"],
    "Maryland": ["Baltimore", "Frederick", "Rockville", "Gaithersburg", "Bowie"],
    "Massachusetts": ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Lansing"],
    "Minnesota": ["Minneapolis", "St. Paul", "Rochester", "Duluth", "Bloomington"],
    "Mississippi": ["Jackson", "Gulfport", "Southaven", "Hattiesburg", "Biloxi"],
    "Missouri": ["Kansas City", "St. Louis", "Springfield", "Columbia", "Independence"],
    "Montana": ["Billings", "Missoula", "Great Falls", "Bozeman", "Butte"],
    "Nebraska": ["Omaha", "Lincoln", "Bellevue", "Grand Island", "Kearney"],
    "Nevada": ["Las Vegas", "Henderson", "Reno", "North Las Vegas", "Sparks"],
    "New Hampshire": ["Manchester", "Nashua", "Concord", "Dover", "Rochester"],
    "New Jersey": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Trenton"],
    "New Mexico": ["Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe", "Roswell"],
    "New York": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem"],
    "North Dakota": ["Fargo", "Bismarck", "Grand Forks", "Minot", "West Fargo"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
    "Oklahoma": ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow", "Edmond"],
    "Oregon": ["Portland", "Salem", "Eugene", "Gresham", "Hillsboro"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading"],
    "Rhode Island": ["Providence", "Warwick", "Cranston", "Pawtucket", "East Providence"],
    "South Carolina": ["Charleston", "Columbia", "North Charleston", "Mount Pleasant", "Rock Hill"],
    "South Dakota": ["Sioux Falls", "Rapid City", "Aberdeen", "Brookings", "Watertown"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville"],
    "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth"],
    "Utah": ["Salt Lake City", "West Valley City", "Provo", "West Jordan", "Orem"],
    "Vermont": ["Burlington", "South Burlington", "Rutland", "Barre", "Montpelier"],
    "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue"],
    "West Virginia": ["Charleston", "Huntington", "Morgantown", "Parkersburg", "Wheeling"],
    "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine"],
    "Wyoming": ["Cheyenne", "Casper", "Laramie", "Gillette", "Rock Springs"]
}

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
                'income_threshold': float(row['income_threshold']),
                'rate': float(row['rate'])
            })
    return rates

def load_state_tax_rates():
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'us_state_tax_rates.csv')
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            state = row['state']
            if year not in rates:
                rates[year] = {}
            if state not in rates[year]:
                rates[year][state] = []
            rates[year][state].append({
                'income_threshold': float(row['income_threshold']),
                'rate': float(row['rate'])
            })
    return rates

def load_local_tax_rates():
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'us_local_tax_rates.csv')
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            if year not in rates:
                rates[year] = {}
            if row['state'] not in rates[year]:
                rates[year][row['state']] = {}
            rates[year][row['state']][row['city']] = float(row['rate'])
    return rates

def load_social_security_rates():
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'us_social_security_rates.csv')
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            rates[year] = {
                'employee_rate': float(row['employee_rate']),
                'employer_rate': float(row['employer_rate']),
                'wage_base': float(row['wage_base'])
            }
    return rates

def load_medicare_rates():
    rates = {}
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'us_medicare_rates.csv')
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = int(row['year'])
            rates[year] = {
                'employee_rate': float(row['employee_rate']),
                'employer_rate': float(row['employer_rate']),
                'additional_rate': float(row['additional_rate']),
                'additional_threshold_single': float(row['additional_threshold_single']),
                'additional_threshold_married': float(row['additional_threshold_married'])
            }
    return rates

FEDERAL_TAX_RATES = load_tax_rates('us_federal_tax_rates.csv')
STATE_TAX_RATES = load_state_tax_rates()
LOCAL_TAX_RATES = load_local_tax_rates()
SOCIAL_SECURITY_RATES = load_social_security_rates()
MEDICARE_RATES = load_medicare_rates()

def get_states():
    return sorted(US_CITIES.keys())

def get_cities(state):
    return US_CITIES.get(state, [])

def get_available_years():
    return sorted(list(FEDERAL_TAX_RATES.keys()), reverse=True)

def calculate_federal_tax(taxable_income, year, is_resident):
    if is_resident:
        tax = 0
        for bracket in FEDERAL_TAX_RATES[year]:
            if taxable_income > bracket['income_threshold']:
                taxable_amount = min(taxable_income, bracket['income_threshold']) - bracket['income_threshold']
                tax += taxable_amount * bracket['rate']
            else:
                break
        return tax
    else:
        # Non-resident aliens are typically taxed at a flat 30% rate on most types of income
        return taxable_income * 0.30

def calculate_state_tax(taxable_income, state, year, is_resident):
    if not is_resident or state not in STATE_TAX_RATES[year]:
        return 0
    tax = 0
    for bracket in STATE_TAX_RATES[year][state]:
        if taxable_income > bracket['income_threshold']:
            taxable_amount = min(taxable_income, bracket['income_threshold']) - bracket['income_threshold']
            tax += taxable_amount * bracket['rate']
        else:
            break
    return tax

def calculate_local_tax(taxable_income, state, city, year, is_resident):
    if not is_resident:
        return 0
    if state in LOCAL_TAX_RATES[year] and city in LOCAL_TAX_RATES[year][state]:
        return taxable_income * LOCAL_TAX_RATES[year][state][city]
    return 0

def calculate_social_security_tax(income, year, is_resident):
    if not is_resident:
        return 0  # Non-resident aliens typically don't pay Social Security tax
    rate = SOCIAL_SECURITY_RATES[year]['employee_rate']
    wage_base = SOCIAL_SECURITY_RATES[year]['wage_base']
    return min(income, wage_base) * rate

def calculate_medicare_tax(income, year, is_resident):
    if not is_resident:
        return 0  # Non-resident aliens typically don't pay Medicare tax
    base_rate = MEDICARE_RATES[year]['employee_rate']
    additional_rate = MEDICARE_RATES[year]['additional_rate']
    threshold = MEDICARE_RATES[year]['additional_threshold_single']
    
    base_tax = income * base_rate
    additional_tax = max(0, (income - threshold) * additional_rate)
    
    return base_tax + additional_tax

def calculate_401k(income, contribution_percent, employer_match_percent, employer_match_limit, is_resident):
    if not is_resident:
        return 0, 0  # Non-resident aliens typically can't contribute to 401(k)
    contribution_limit = 23000  # 2024 401(k) contribution limit
    contribution = min(income * (contribution_percent / 100), contribution_limit)
    
    employer_contribution = min(
        contribution,
        income * (employer_match_percent / 100),
        income * (employer_match_limit / 100)
    )
    
    return contribution, employer_contribution

def calculate(income, state, city, year, is_resident=True, contribution_percent=0, employer_match_percent=0, employer_match_limit=0):
    if year not in FEDERAL_TAX_RATES:
        raise ValueError(f"No data available for year {year}")

    # Calculate 401(k) contributions
    employee_401k, employer_401k = calculate_401k(income, contribution_percent, employer_match_percent, employer_match_limit, is_resident)
    
    # Adjust taxable income
    taxable_income = income - employee_401k

    federal_tax = calculate_federal_tax(taxable_income, year, is_resident)
    state_tax = calculate_state_tax(taxable_income, state, year, is_resident)
    local_tax = calculate_local_tax(taxable_income, state, city, year, is_resident)
    social_security_tax = calculate_social_security_tax(income, year, is_resident)
    medicare_tax = calculate_medicare_tax(income, year, is_resident)

    total_tax = federal_tax + state_tax + local_tax + social_security_tax + medicare_tax
    net_income = income - total_tax - employee_401k

    breakdown = {
        'country': 'United States',
        'year': year,
        'is_resident': is_resident,
        'gross_income': income,
        'taxable_income': taxable_income,
        'federal_tax': federal_tax,
        'state_tax': state_tax,
        'local_tax': local_tax,
        'social_security_tax': social_security_tax,
        'medicare_tax': medicare_tax,
        'total_tax': total_tax,
        'employee_401k_contribution': employee_401k,
        'employer_401k_contribution': employer_401k,
        'net_income': net_income,
        'total_compensation': income + employer_401k
    }

    return breakdown