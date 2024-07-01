from . import sg_calc, us_calc, cn_calc

calculators = {
    'Singapore': sg_calc,
    'United States': us_calc,
    'China': cn_calc,
}

def get_calculator(country):
    return calculators.get(country)

def get_available_countries():
    return list(calculators.keys())

def get_available_years():
    years = set()
    for calculator in calculators.values():
        years.update(calculator.get_available_years())
    return sorted(list(years), reverse=True)